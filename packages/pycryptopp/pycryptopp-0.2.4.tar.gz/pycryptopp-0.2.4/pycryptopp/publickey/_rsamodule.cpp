/**
 * _rsamodule.cpp -- Python wrappers around Crypto++'s RSA-PSS-SHA256
 * more precisely:
 * <a href="http://www.weidai.com/scan-mirror/sig.html#sem_PSS-MGF1">PSS-MGF1</a>
 * with RSA as the public key algorithm and SHA-256 as the hash function
 */

#include <Python.h>

#if (PY_VERSION_HEX < 0x02050000)
typedef int Py_ssize_t;
#endif

/* from Crypto++ */
#ifdef USE_NAME_CRYPTO_PLUS_PLUS
// for Debian (and Ubuntu, and their many derivatives)
#include "crypto++/filters.h"
#include "crypto++/osrng.h"
#include "crypto++/pssr.h"
#include "crypto++/rsa.h"
#else
// for upstream Crypto++ library
#include "cryptopp/filters.h"
#include "cryptopp/osrng.h"
#include "cryptopp/pssr.h"
#include "cryptopp/rsa.h"
#endif

USING_NAMESPACE(CryptoPP)

PyDoc_STRVAR(rsa__doc__,
"rsa -- RSA-PSS-SHA256 signatures\n\
\n\
To create a new RSA signing key from the operating system's random number generator, call generate().\n\
To create a new RSA signing key from a seed, call generate_from_seed().\n\
To deserialize an RSA signing key from a string, call create_signing_key_from_string().\n\
\n\
To get an RSA verifying key from an RSA signing key, call get_verifying_key() on the signing key.\n\
To deserialize an RSA verifying key from a string, call create_verifying_key_from_string().");

static PyObject *rsa_error;

typedef struct {
    PyObject_HEAD

    /* internal */
    RSASS<PSS, SHA256>::Verifier *k;
} VerifyingKey;

PyDoc_STRVAR(VerifyingKey__doc__,
"an RSA verifying key");

static void
VerifyingKey_dealloc(VerifyingKey* self) {
    if (self->k != NULL)
        delete self->k;
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
VerifyingKey_verify(VerifyingKey *self, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = { "msg", "signature", NULL };
    const char *msg;
    size_t msgsize;
    const char *signature;
    size_t signaturesize;
    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "s#s#:verify", const_cast<char**>(kwlist), &msg, &msgsize, &signature, &signaturesize))
        return NULL;

    size_t sigsize = self->k->SignatureLength();
    if (sigsize != signaturesize)
        return PyErr_Format(rsa_error, "Precondition violation: signatures are required to be of size %u, but it was %u", sigsize, signaturesize);

    assert (signaturesize == sigsize);

    if (self->k->VerifyMessage(reinterpret_cast<const byte*>(msg), msgsize, reinterpret_cast<const byte*>(signature), signaturesize))
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

PyDoc_STRVAR(VerifyingKey_verify__doc__,
"Return whether the signature is a valid signature on the msg.");

static PyObject *
VerifyingKey_serialize(VerifyingKey *self, PyObject *dummy) {
    std::string outstr;
    StringSink ss(outstr);
    self->k->DEREncode(ss);
    PyStringObject* result = reinterpret_cast<PyStringObject*>(PyString_FromStringAndSize(outstr.c_str(), outstr.size()));
    if (!result)
        return NULL;

    return reinterpret_cast<PyObject*>(result);
}

PyDoc_STRVAR(VerifyingKey_serialize__doc__,
"Return a string containing the key material.  The string can be passed to \n\
create_verifying_key_from_string() to instantiate a new copy of this key.");

static PyMethodDef VerifyingKey_methods[] = {
    {"verify", reinterpret_cast<PyCFunction>(VerifyingKey_verify), METH_KEYWORDS, VerifyingKey_verify__doc__},
    {"serialize", reinterpret_cast<PyCFunction>(VerifyingKey_serialize), METH_NOARGS, VerifyingKey_serialize__doc__},
    {NULL},
};

static PyTypeObject VerifyingKey_type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_rsa.VerifyingKey", /*tp_name*/
    sizeof(VerifyingKey),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    reinterpret_cast<destructor>(VerifyingKey_dealloc), /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    VerifyingKey__doc__,           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    VerifyingKey_methods,             /* tp_methods */
};

/** This function is only for internal use by _rsamodule.cpp. */
static VerifyingKey*
VerifyingKey_construct() {
    VerifyingKey *self = reinterpret_cast<VerifyingKey*>(VerifyingKey_type.tp_alloc(&VerifyingKey_type, 0));
    self->k = NULL;
    return self;
}

PyDoc_STRVAR(SigningKey__doc__,
"an RSA signing key");

typedef struct {
    PyObject_HEAD

    /* internal */
    RSASS<PSS, SHA256>::Signer *k;
} SigningKey;

static void
SigningKey_dealloc(SigningKey* self) {
    if (self->k)
        delete self->k;
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
SigningKey_sign(SigningKey *self, PyObject *msgobj) {
    const char *msg;
    size_t msgsize;
    PyString_AsStringAndSize(msgobj, const_cast<char**>(&msg), reinterpret_cast<Py_ssize_t*>(&msgsize));

    size_t sigsize = self->k->SignatureLength();
    PyStringObject* result = reinterpret_cast<PyStringObject*>(PyString_FromStringAndSize(NULL, sigsize));
    if (!result)
        return NULL;

    AutoSeededRandomPool randpool(false);
    size_t siglengthwritten = self->k->SignMessage(
        randpool,
        reinterpret_cast<const byte*>(msg),
        msgsize,
        reinterpret_cast<byte*>(PyString_AS_STRING(result)));
    if (siglengthwritten < sigsize)
        fprintf(stderr, "%s: %d: %s: %s", __FILE__, __LINE__, __func__, "INTERNAL ERROR: signature was shorter than expected.");
    else if (siglengthwritten > sigsize) {
        fprintf(stderr, "%s: %d: %s: %s", __FILE__, __LINE__, __func__, "INTERNAL ERROR: signature was longer than expected, so invalid memory was overwritten.");
        abort();
    }

    return reinterpret_cast<PyObject*>(result);
}

PyDoc_STRVAR(SigningKey_sign__doc__,
"Return a signature on the argument.");

static PyObject *
SigningKey_get_verifying_key(SigningKey *self, PyObject *dummy) {
    VerifyingKey *verifier = reinterpret_cast<VerifyingKey*>(VerifyingKey_construct());
    if (!verifier)
        return NULL;

    verifier->k = new RSASS<PSS, SHA256>::Verifier(*(self->k));
    if (verifier->k)
        return reinterpret_cast<PyObject*>(verifier);
    else
        return NULL;
}

PyDoc_STRVAR(SigningKey_get_verifying_key__doc__,
"Return the corresponding verifying key.");

static PyObject *
SigningKey_serialize(SigningKey *self, PyObject *dummy) {
    std::string outstr;
    StringSink ss(outstr);
    self->k->DEREncode(ss);
    PyStringObject* result = reinterpret_cast<PyStringObject*>(PyString_FromStringAndSize(outstr.c_str(), outstr.size()));
    if (!result)
        return NULL;

    return reinterpret_cast<PyObject*>(result);
}

PyDoc_STRVAR(SigningKey_serialize__doc__,
"Return a string containing the key material.  The string can be passed to \n\
create_signing_key_from_string() to instantiate a new copy of this key.");

static PyMethodDef SigningKey_methods[] = {
    {"sign", reinterpret_cast<PyCFunction>(SigningKey_sign), METH_O, SigningKey_sign__doc__},
    {"get_verifying_key", reinterpret_cast<PyCFunction>(SigningKey_get_verifying_key), METH_NOARGS, SigningKey_get_verifying_key__doc__},
    {"serialize", reinterpret_cast<PyCFunction>(SigningKey_serialize), METH_NOARGS, SigningKey_serialize__doc__},
    {NULL},
};

static PyTypeObject SigningKey_type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_rsa.SigningKey", /*tp_name*/
    sizeof(SigningKey),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)SigningKey_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    SigningKey__doc__,           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    SigningKey_methods             /* tp_methods */
};

/** This function is only for internal use by _rsamodule.cpp. */
static SigningKey*
SigningKey_construct() {
    SigningKey *self = reinterpret_cast<SigningKey*>(SigningKey_type.tp_alloc(&SigningKey_type, 0));
    self->k = NULL;
    return self;
}

// static const int MIN_KEY_SIZE_BITS=3675; /* according to Lenstra 2001 "Unbelievable security: Matching AES security using public key systems", you should use RSA keys of length 3675 bits if you want it to be as hard to factor your RSA key as to brute-force your AES-128 key in the year 2030. */
static const int MIN_KEY_SIZE_BITS=522; /* minimum that can do PSS-SHA256 -- totally insecure and allowed only for faster unit tests */

static PyObject*
generate_from_seed(PyObject *dummy, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = {
        "sizeinbits",
        "seed",
        NULL
    };
    int sizeinbits;
    const char* seed;
    int seedlen;
    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "is#:generate_from_seed", const_cast<char**>(kwlist), &sizeinbits, &seed, &seedlen))
        return NULL;

    if (sizeinbits < MIN_KEY_SIZE_BITS)
        return PyErr_Format(rsa_error, "Precondition violation: size in bits is required to be >= %u, but it was %d", MIN_KEY_SIZE_BITS, sizeinbits);

    if (seedlen < 8)
        return PyErr_Format(rsa_error, "Precondition violation: seed is required to be of length >= %u, but it was %d", 8, seedlen);

    RandomPool randPool;
    randPool.Put((byte *)seed, seedlen); /* In Crypto++ v5.5.2, the recommended interface is "IncorporateEntropy()", but "Put()" is supported for backwards compatibility.  In Crypto++ v5.2 (the version that comes with Ubuntu dapper), only "Put()" is available. */

    SigningKey *signer = SigningKey_construct();
    if (!signer)
        return NULL;
    signer->k = new RSASS<PSS, SHA256>::Signer(randPool, sizeinbits);
    return reinterpret_cast<PyObject*>(signer);
}

PyDoc_STRVAR(generate_from_seed__doc__,
"Create a signing key deterministically from the given seed.\n\
\n\
This implies that if someone can guess the seed then they can learn the signing key.\n\
See also generate().\n\
\n\
@param sizeinbits size of the key in bits\n\
@param seed seed\n\
\n\
@precondition sizeinbits >= 1536\n\
@precondition len(seed) >= 8");

static PyObject *
generate(PyObject *dummy, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = {
        "sizeinbits",
        NULL
    };
    int sizeinbits;

    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "i:generate", const_cast<char**>(kwlist), &sizeinbits))
        return NULL;

    if (sizeinbits < MIN_KEY_SIZE_BITS)
        return PyErr_Format(rsa_error, "Precondition violation: size in bits is required to be >= %u, but it was %d", MIN_KEY_SIZE_BITS, sizeinbits);

    AutoSeededRandomPool osrng(false);
    SigningKey *signer = SigningKey_construct();
    if (!signer)
        return NULL;
    signer->k = new RSASS<PSS, SHA256>::Signer(osrng, sizeinbits);
    return reinterpret_cast<PyObject*>(signer);
}

PyDoc_STRVAR(generate__doc__,
"Create a signing key using the operating system's random number generator.");

static PyObject *
create_verifying_key_from_string(PyObject *dummy, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = {
        "serializedverifyingkey",
        NULL
    };
    const char *serializedverifyingkey;
    size_t serializedverifyingkeysize;

    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "s#:create_verifying_key_from_string", const_cast<char**>(kwlist), &serializedverifyingkey, &serializedverifyingkeysize))
        return NULL;

    VerifyingKey *verifier = reinterpret_cast<VerifyingKey*>(VerifyingKey_construct());
    if (!verifier)
        return NULL;
    StringSource ss(reinterpret_cast<const byte*>(serializedverifyingkey), serializedverifyingkeysize, true);

    verifier->k = new RSASS<PSS, SHA256>::Verifier(ss);
    return reinterpret_cast<PyObject*>(verifier);
}

PyDoc_STRVAR(create_verifying_key_from_string__doc__,
"Create a verifying key from its serialized state.");

static PyObject *
create_signing_key_from_string(PyObject *dummy, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = {
        "serializedsigningkey",
        NULL
    };
    const char *serializedsigningkey;
    size_t serializedsigningkeysize;

    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "s#:create_signing_key_from_string", const_cast<char**>(kwlist), &serializedsigningkey, &serializedsigningkeysize))
        return NULL;

    SigningKey *verifier = SigningKey_construct();
    if (!verifier)
        return NULL;
    StringSource ss(reinterpret_cast<const byte*>(serializedsigningkey), serializedsigningkeysize, true);

    verifier->k = new RSASS<PSS, SHA256>::Signer(ss);
    return reinterpret_cast<PyObject*>(verifier);
}

PyDoc_STRVAR(create_signing_key_from_string__doc__,
"Create a signing key from its serialized state.");

static PyMethodDef rsa_functions[] = { 
    {"generate_from_seed", reinterpret_cast<PyCFunction>(generate_from_seed), METH_KEYWORDS, generate_from_seed__doc__},
    {"generate", reinterpret_cast<PyCFunction>(generate), METH_KEYWORDS, generate__doc__},
     {"create_verifying_key_from_string", reinterpret_cast<PyCFunction>(create_verifying_key_from_string), METH_KEYWORDS, create_verifying_key_from_string__doc__},
     {"create_signing_key_from_string", reinterpret_cast<PyCFunction>(create_signing_key_from_string), METH_KEYWORDS, create_signing_key_from_string__doc__},
    {NULL, NULL, 0, NULL}  /* sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_rsa(void) {
    PyObject *module;
    PyObject *module_dict;

    if (PyType_Ready(&VerifyingKey_type) < 0)
        return;
    if (PyType_Ready(&SigningKey_type) < 0)
        return;

    module = Py_InitModule3("_rsa", rsa_functions, rsa__doc__);
    if (!module)
      return;

    Py_INCREF(&SigningKey_type);
    Py_INCREF(&VerifyingKey_type);

    PyModule_AddObject(module, "SigningKey", (PyObject *)&SigningKey_type);
    PyModule_AddObject(module, "VerifyingKey", (PyObject *)&VerifyingKey_type);

    module_dict = PyModule_GetDict(module);
    rsa_error = PyErr_NewException("_rsa.Error", NULL, NULL);
    PyDict_SetItemString(module_dict, "Error", rsa_error);
}
