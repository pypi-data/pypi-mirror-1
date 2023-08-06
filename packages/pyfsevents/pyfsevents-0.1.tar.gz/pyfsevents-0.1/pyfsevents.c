/*
 * pyfsevents.c - Python extension interfacing to the Mac OS FSevents API
 *
 * Copyright 2009 Nicolas Dumazet <nicdumz@gmail.com>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the MIT License.
 */

#include <Python.h>
#include <CoreFoundation/CoreFoundation.h>
#include <CoreServices/CoreServices.h>
#include <signal.h>


/*
 * Data kept when watching a file descriptor
 */
typedef struct {
    int mask;
    CFRunLoopSourceRef source;
    CFFileDescriptorRef desc;
    PyObject* callback;
} FDInfo;

/*
 * Data kept when watching a path through FSevents
 */
typedef struct {
    FSEventStreamRef stream;
    PyObject* callback;
} FSEventInfo;

/* dictionary that will contain per-(fd/path) info */
PyObject* dict = NULL;

/*
 * Helper function to log errors
 */
static void LogError(const char *format, ...) {
    va_list ap;
    va_start(ap, format);
    (void) vfprintf(stderr, format, ap);
    va_end(ap);
}

/*
 * Signal handler for SIGINT
 */
static void sighandler(int sig) {
    CFRunLoopStop(CFRunLoopGetCurrent());
    PyErr_SetString(PyExc_KeyboardInterrupt, "");
}


/*
 * Callback that is registered to the FSEvents API
 */
static void fsevents_callback(
    FSEventStreamRef streamRef,
    void *clientCallBackInfo,
    int numEvents,
    const char *const eventPaths[],
    const FSEventStreamEventFlags *eventMasks,
    const uint64_t *eventIDs) {

    int i;
    PyObject *scanSub;

    PyObject* key = (PyObject*) clientCallBackInfo;

    PyObject* cobj = PyDict_GetItem(dict, key);
    FSEventInfo* info = (FSEventInfo*) PyCObject_AsVoidPtr(cobj);

    if (PyErr_Occurred()) {
        CFRunLoopStop(CFRunLoopGetCurrent());
        return;
    }

    /* for each event, fire the callback */
    for (i=0; i < numEvents; i++) {
        scanSub = PyBool_FromLong(
                    eventMasks[i] & kFSEventStreamEventFlagMustScanSubDirs
                  );

        if (PyObject_CallFunction(info->callback, "sN", eventPaths[i],
                scanSub) == NULL) {
            // CallFunction can return NULL if an exception is raised.
            // If not, the interpreter could not call the function
            if (!PyErr_Occurred()) LogError("Failed to call callback\n");
            // Whatever is the reason, stop listening.
            CFRunLoopStop(CFRunLoopGetCurrent());
        }
    }
}

/*
 * Callback for file descriptor events.
 */
static void fd_callback(
    CFFileDescriptorRef fdref,
    CFOptionFlags callBackTypes,
    void* key) {

    int fd = CFFileDescriptorGetNativeDescriptor(fdref);

    PyObject* pyfd = (PyObject*) key;
    PyObject* cobj = PyDict_GetItem(dict, pyfd);
    FDInfo* info = (FDInfo*) PyCObject_AsVoidPtr(cobj);

    if (PyErr_Occurred()) {
        CFRunLoopStop(CFRunLoopGetCurrent());
        return;
    }

    if (info->mask & callBackTypes) {

        if (PyObject_CallFunction(info->callback, "II", fd,
                (unsigned int) callBackTypes) == NULL) {
            if (!PyErr_Occurred()) LogError("Failed to call callback\n");
            CFRunLoopStop(CFRunLoopGetCurrent());
            return;
        }
    }
    // CFFileDescriptor events are fire-once callbacks and get
    // desactivated on first event. Reactivate callbacks.
    CFFileDescriptorEnableCallBacks(fdref, info->mask);
}


/*
 * Simple wrapper to create an FSEventStream
 */
static FSEventStreamRef my_FSEventStreamCreate(PyStringObject *pypath) {
    FSEventStreamContext  context = {0, (void*) pypath, NULL, NULL, NULL};
    FSEventStreamRef      streamRef = NULL;
    CFMutableArrayRef     cfArray;

    const char* path = PyString_AS_STRING(pypath);

    cfArray = CFArrayCreateMutable(kCFAllocatorDefault, 1, &kCFTypeArrayCallBacks);
    if (NULL == cfArray) {
        LogError("%s: ERROR: CFArrayCreateMutable() => NULL\n", __FUNCTION__);
        goto Return;
    }

    CFStringRef cfStr = CFStringCreateWithCString(kCFAllocatorDefault, path, kCFStringEncodingUTF8);
    if (NULL == cfStr) {
        CFRelease(cfArray);
        goto Return;
    }

    CFArraySetValueAtIndex(cfArray, 0, cfStr);
    CFRelease(cfStr);

    streamRef = FSEventStreamCreate(kCFAllocatorDefault,
                                    (FSEventStreamCallback)&fsevents_callback,
                                    &context,
                                    cfArray,
                                    kFSEventStreamEventIdSinceNow,
                                    0.01, // latency
                                    kFSEventStreamCreateFlagNoDefer);
    CFRelease(cfArray);
    if (NULL == streamRef) {
        LogError("%s: ERROR: FSEventStreamCreate() => NULL\n", __FUNCTION__);
    }

Return:
    return streamRef;
}


/* Python Functions */


/*
 * register the path to watch, initialize the event list
 * Arguments:
 *  - string: the absolute path to watch
 *  - callable: the callback to fire on events
 */
static PyObject* pyfsevents_registerpath(PyObject* self, PyObject* args) {
    PyStringObject* path;
    PyObject* callback;

    if (!PyArg_ParseTuple(args, "SO:registerpath", &path, &callback))
        return NULL;

    Py_INCREF(callback);
    FSEventInfo *info = PyMem_New(FSEventInfo, 1);
    if (info == NULL)
        return PyErr_NoMemory();

    info->callback = callback;

    FSEventStreamRef stream = my_FSEventStreamCreate(path);
    if (stream == NULL) {
        LogError("Failed to create the FSEventStream\n");
        return NULL;
    }

    FSEventStreamScheduleWithRunLoop(stream, CFRunLoopGetCurrent(), kCFRunLoopDefaultMode);

    if (!FSEventStreamStart(stream)) {
        LogError("%s: failed to start the FSEventStream\n");
        FSEventStreamInvalidate(stream);
        FSEventStreamRelease(stream);
        return NULL;
    }

    info->stream = stream;
    PyObject* value = PyCObject_FromVoidPtr((void*) info, PyMem_Free);
    int err = PyDict_SetItem(dict, (PyObject*) path, value);
    Py_DECREF(value);
    if (err)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

PyDoc_STRVAR(
    registerpath_doc,
    "registerpath(abspath, callback)\n\n"
    "Register the path to the FS events watcher.\n\n"

    "abspath is the absolute path to watch\n\n"
    
    "callback is the callback that will be fired on events.\n\n"

    "The callback function should have a (path, isrec) signature, where path\n"
    "is the directory where an event occurred, and isrec a boolean: if isrec\n"
    "is True, users should scan recursively subdirectories for events\n");

/*
 * Register a file descriptor
 * Arguments:
 *  - int or object with a fileno() method
 *  - callable: callback to fire on events
 *  - optional int mask
 */
static PyObject* pyfsevents_registerfd(PyObject* self, PyObject* args) {
    PyObject *param, *callback;
    int mask = kCFFileDescriptorReadCallBack | kCFFileDescriptorWriteCallBack;

    if (!PyArg_ParseTuple(args, "OO|i:register", &param, &callback, &mask))
        return NULL;
    Py_INCREF(callback);

    int fd = PyObject_AsFileDescriptor(param);
    if (fd == -1)
        return NULL;

    PyObject *key = PyInt_FromLong(fd);
    if (key == NULL)
        return NULL;

    FDInfo *info;
    PyObject *value = PyDict_GetItem(dict, key);
    if (value == NULL) {
        // the fs was not yet registered
        info = PyMem_New(FDInfo, 1);
        if (info == NULL)
            return PyErr_NoMemory();

        info->callback = callback;

        CFFileDescriptorContext context = {0, key, NULL, NULL, NULL};
        CFFileDescriptorRef fdref;
        CFRunLoopSourceRef source;

        fdref = CFFileDescriptorCreate(NULL,
                fd,
                false,
                (CFFileDescriptorCallBack) fd_callback,
                &context);
        if (fdref == NULL) {
            LogError("Failed to create the CFFileDescriptor\n");
            goto bail;
        }

        CFFileDescriptorEnableCallBacks(fdref, mask);

        source = CFFileDescriptorCreateRunLoopSource(kCFAllocatorDefault,
                fdref, 0);
        if (source == NULL) {
            LogError("Failed to create the RunLoop Source\n");
            goto bail;
        }

        info->source = source;
        info->desc = fdref;
        info->mask = mask;

        value = PyCObject_FromVoidPtr((void*) info, PyMem_Free);
        int err = PyDict_SetItem(dict, key, value);
        Py_DECREF(value);
        if (err)
            goto bail;

        CFRunLoopAddSource(CFRunLoopGetCurrent(),
                source, kCFRunLoopDefaultMode);
    } else {
        // that fd was already registered, just update the mask
        info = (FDInfo*) PyCObject_AsVoidPtr(value);
        info->mask = mask;
        info->callback = callback;
        CFFileDescriptorEnableCallBacks(info->desc, mask);
    }

    Py_INCREF(Py_None);
    return Py_None;

bail:
    PyMem_Free(info);
    return NULL;
}

PyDoc_STRVAR(
    registerfd_doc,
    "register(fd, callback, [, eventmask])\n\n"

    "Register a file descriptor.\n\n"

    "fd can eiter be an integer, or an object that has a fileno() method that\n"
    "returns an integer.\n\n"

    "callback is the callback that will be fired on events.\n\n"

    "eventmask is an optional bitmask, which can be a combination of the \n"
    "constants POLLIN, and POLLOUT, similarly to select.poll. If not \n"
    "specified, the default value will check for both types of events\n\n"

    "The callback function should have a (fd, mask) signature, where fd is\n"
    "the file descriptor raising the event, and mask the event mask");


/*
 * Listen for events. Fires callbacks on events.
 */
static PyObject* pyfsevents_listen(PyObject* self, PyObject* args) {

    PyOS_sighandler_t handler = signal(SIGINT, sighandler);

    // No timeout, block until events
    CFRunLoopRun();

    if (handler != SIG_ERR)
        signal(SIGINT, handler);

    if (PyErr_Occurred()) return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

PyDoc_STRVAR(
    listen_doc,
    "listen()\n\n"
    "Blocking call listening for events.\n"
    "Fires callbacks on events");


/*
 * Invalidate and release sources/streams
 * key, cobj is the key, value pair that was in the dict
 */
static void removesource(PyObject *key, PyObject *cobj) {
    void *info = PyCObject_AsVoidPtr(cobj);

    if (PyString_Check(key)) {
        /* FSEvents path */
        FSEventStreamRef stream = ((FSEventInfo*)info)->stream;
        FSEventStreamStop(stream);
        FSEventStreamInvalidate(stream);
        FSEventStreamRelease(stream);
    } else if(PyInt_Check(key)) {
        /* file descriptor */
        CFRunLoopSourceRef source = ((FDInfo*)info)->source;
        CFRunLoopSourceInvalidate(source);
        CFRunLoopRemoveSource(CFRunLoopGetCurrent(),
                              source,
                              kCFRunLoopDefaultMode);
        CFRelease(source);
    }
}

/*
 * Given a key from the dict, unregister the associated
 * fd or path
 */
static PyObject* generic_unregister(PyObject* key) {
    PyObject* value = PyDict_GetItem(dict, key);
    if (value != NULL) {
        removesource(key, value);
    }

    if (PyDict_DelItem(dict, key) == -1) {
        Py_DECREF(key);
        /* raise */
        return NULL;
    }
    Py_DECREF(key);

    Py_INCREF(Py_None);
    return Py_None;
}

/*
 * Unregister a file descriptor
 */
static PyObject* pyfsevents_unregisterfd(PyObject* self, PyObject* o) {
    int fd = PyObject_AsFileDescriptor(o);
    if (fd == -1)
        return NULL;

    PyObject *key = PyInt_FromLong(fd);
    if (key == NULL)
        return NULL;

    return generic_unregister(key);
}

PyDoc_STRVAR(
    unregisterfd_doc,
    "unregisterfd(fd)\n\n"
    "Unregisters a file descriptor.");

/*
 * Unregister a fsevents path
 */
static PyObject* pyfsevents_unregisterpath(PyObject* self, PyObject* args) {
    PyObject *path;

    if (!PyArg_ParseTuple(args, "S:unregisterpath", &path))
        return NULL;
    Py_INCREF(path);

    return generic_unregister(path);
}

PyDoc_STRVAR(
    unregisterpath_doc,
    "unregister(abspath)\n\n"
    "Unregisters a FSEvent path.");

/*
 * Remove all sources
 */
static PyObject* pyfsevents_clear(PyObject* self, PyObject* o) {
    PyObject *key, *value;
    Py_ssize_t pos = 0;

    while (PyDict_Next(dict, &pos, &key, &value))
        removesource(key, value);

    PyDict_Clear(dict);

    Py_INCREF(Py_None);
    return Py_None;
}

PyDoc_STRVAR(
    clear_doc,
    "clear()\n\n"
    "Unregister all the file descriptors and FSEvent paths");

/*
 * Stop listening
 */
static PyObject* pyfsevents_stop(PyObject* self, PyObject* o) {
    CFRunLoopStop(CFRunLoopGetCurrent());
    Py_INCREF(Py_None);
    return Py_None;
}

PyDoc_STRVAR(
    stop_doc,
    "stop()\n\n"
    "stops the listener");


static PyMethodDef methods[] = {
    {"registerpath",
        pyfsevents_registerpath, METH_VARARGS, registerpath_doc},
    {"registerfd",
        pyfsevents_registerfd, METH_VARARGS, registerfd_doc},
    {"listen",
        pyfsevents_listen, METH_NOARGS, listen_doc},
    {"unregisterpath",
        pyfsevents_unregisterpath, METH_VARARGS, unregisterpath_doc},
    {"unregisterfd",
        pyfsevents_unregisterfd, METH_O, unregisterfd_doc},
    {"clear",
        pyfsevents_clear, METH_NOARGS, clear_doc},
    {"stop",
        pyfsevents_stop, METH_NOARGS, stop_doc},
    {NULL},
};

static char doc[] = "Low-level FSEvent interface";

PyMODINIT_FUNC initpyfsevents(void) {
    PyObject* mod = Py_InitModule3("pyfsevents", methods, doc);
    PyModule_AddIntConstant(mod, "POLLIN", kCFFileDescriptorReadCallBack);
    PyModule_AddIntConstant(mod, "POLLOUT", kCFFileDescriptorWriteCallBack);

    dict = PyDict_New();
}

