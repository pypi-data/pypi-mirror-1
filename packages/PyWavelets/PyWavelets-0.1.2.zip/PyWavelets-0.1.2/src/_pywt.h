extern DL_IMPORT(PyTypeObject) WaveletType;

struct WaveletObject {
  PyObject_HEAD
  Wavelet (*w);
  PyObject *name;
  PyObject *number;
};
extern DL_IMPORT(void) init_pywt(void);
