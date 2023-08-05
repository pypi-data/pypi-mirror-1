#include <Python.h>
#include <security/pam_appl.h>
#define PY_DEF(name) static PyObject *(name)(PyObject *self, PyObject *args)

typedef struct {
	char* username;
	char* password;
} spypam_creds;

typedef struct {
	pam_handle_t *pamh;
	struct pam_conv *conv;
} spypam_tconv;

void *evil_ptr = NULL;

/**
 * XXX: Obvious memory leak in spypam_conv.
 * 		I don't know when I should free the pam_response that I return to pam,
 * 		but somewhere after the negotiation is done anyway. Would imply
 * 		that I have to store the pointer to that memory area somewhere
 * 		and to ugly things. I don't know how to go about this. Perhaps
 * 		add that same pointer in spypam_creds (and rename it) so that
 * 		I can free it taking the value of the appdata_ptr later in the
 * 		main authentication loop?
 *
 * 		Meh. Ugly. (Fixed, ugly.)
 */

static int spypam_conv(int msgc, const struct pam_message** msgv,
		struct pam_response** response, void* appdata_ptr) {
	
	spypam_creds* creds = (spypam_creds*)appdata_ptr;
	int i;
	char* resp_str = NULL;
	struct pam_response* tresp;

	if (!creds || !msgc) return PAM_CONV_ERR;
	
	if (!(tresp = calloc(sizeof(struct pam_response), msgc))) {
		return PAM_CONV_ERR;
	}
    
	for (i = 0; i < msgc; i++) {
		resp_str = NULL;
		switch (msgv[i]->msg_style) {
			case PAM_PROMPT_ECHO_OFF:
				resp_str = creds->password;
				break;

			case PAM_PROMPT_ECHO_ON:
				resp_str = creds->username;
				break;
		}
		if (resp_str) {
			tresp[i].resp = resp_str;
			tresp[i].resp_retcode = 0;
		}
	}
	
	/* This sets the pointer pointed to by response to tresp. */
	*response = tresp;
	evil_ptr = tresp;
	return PAM_SUCCESS;
}

static PyObject* spypam_authenticate_simple(PyObject* self, PyObject* args) {
	char *service, *username, *password;
	int r;
	pam_handle_t* pamh;
	struct pam_conv conv;

	spypam_creds* creds;
	PyObject* ret;

	if (!PyArg_ParseTuple(args, "sss", &service, &username, &password)) {
		return NULL;
	}

	ret = Py_False;
	
	if (service[0] != '\0' && username[0] != '\0') {
		if (!(creds = malloc(sizeof(spypam_creds)))) {
			return PyErr_NoMemory();
		}

		creds->username = strdup(username); /* Don't use the args refs */
		creds->password = strdup(password);

		conv.conv = &spypam_conv;
		conv.appdata_ptr = creds;
		
		/* pam_start allocates memory for pamh. */
		if ((r = pam_start(service, username, &conv, &pamh)) == PAM_SUCCESS) {
			if ((r = pam_authenticate(pamh, 0)) == PAM_SUCCESS) {
				r = pam_acct_mgmt(pamh, 0);
			}
		}
		pam_end(pamh, r); /* pam_end frees pamh. */
		pamh = NULL;
		/* For some reason I can't free the members of creds. */
		free(creds);
		creds = NULL;
		if (r == PAM_SUCCESS) ret = Py_True;
		/* Evil part starts here: We free memory that we did not allocate.
		 * We also rely on the fact that calling free() on a NULL pointer
		 * does nothing. */
		free(evil_ptr);
		evil_ptr = NULL;
	}
	
	Py_INCREF(ret);
	return ret;
}

static PyObject *spypam_pam_start(PyObject *self, PyObject *args) {
	char *service;
	char *username;
	spypam_tconv *tconv;

	printf("ZOMG :D\n");
	if (!PyArg_ParseTuple(args, "ss", &service, &username)) {
		return NULL;
	}
	printf("ZOMG AGAIN :D\n");
	tconv = malloc(sizeof(spypam_tconv));
	tconv->conv = malloc(sizeof(struct pam_conv));
	tconv->conv->conv = &spypam_conv;
	tconv->conv->appdata_ptr = malloc(sizeof(spypam_creds));
	printf("WOMG AGAIN %s, %s :<\n", service, username);
	/* Hopefully pam_start doesn't use service/username; they're eaten. */
	if (pam_start(service, username, tconv->conv, &(tconv->pamh)) != PAM_SUCCESS) {
		printf("NO RETURN :>\n");
		PyErr_SetString(PyExc_RuntimeError, "Failed to start PAM.");
		return NULL;
	}
	printf("RETURN :>\n");
	printf("RETURN %d:>\n", (long)tconv);
	return PyInt_FromLong((long)tconv);
}

static PyObject *spypam_pam_end(PyObject *self, PyObject *args) {
	spypam_tconv *tconv;
	PyObject *r = Py_True;

	if (!PyArg_ParseTuple(args, "k", &tconv)) {
		return NULL;
	}
	
	if (pam_end((pam_handle_t *)tconv->pamh, 0) != PAM_SUCCESS) {
		r = Py_False;
	}

	if (tconv->conv->appdata_ptr) {
		spypam_creds *c;
		c = tconv->conv->appdata_ptr;
		free(c->username);
		free(c->password);
		free(c);
	}
	free(tconv->conv);
	free(tconv);

	Py_INCREF(r);
	return r;
}

static PyObject *spypam_session_open(PyObject *self, PyObject *args) {
	spypam_tconv *tconv;
	int flags;
	PyObject *r;

	if (!PyArg_ParseTuple(args, "ki", &tconv, &flags)) {
		return NULL;
	}

	r = ((pam_open_session(tconv->pamh, flags) != PAM_SUCCESS) ? 
		Py_True : Py_True);
	Py_INCREF(r);
	return r;
}

static PyObject *spypam_session_close(PyObject *self, PyObject *args) {
	spypam_tconv *tconv;
	int flags;
	PyObject *r;

	if (!PyArg_ParseTuple(args, "ki", &tconv, &flags)) {
		return NULL;
	}

	r = ((pam_close_session(tconv->pamh, flags) != PAM_SUCCESS) ? 
		Py_True : Py_True);
	Py_INCREF(r);
	return r;
}

static PyObject *spypam_set_creds(PyObject *self, PyObject *args) {
	spypam_tconv *tconv;
	spypam_creds *creds;
	char *username;
	char *password;

	if (!PyArg_ParseTuple(args, "kss", &tconv, &username, &password)) {
		return NULL;
	}

	/* Okay fine, creds isn't really valuable here, but I'm 1) lazy and
	 * 2) gcc whines, anyway - should be fine. */
	creds = tconv->conv->appdata_ptr;
	creds->username = strdup(username);
	creds->password = strdup(password);

	Py_RETURN_NONE;
}

PY_DEF(spypam_authenticate) {
	spypam_tconv *tconv;
	int flags;
	int r;

	if (!PyArg_ParseTuple(args, "ki", &tconv, &flags)) {
		return NULL;
	}
	
	if (!tconv->conv->appdata_ptr) {
		PyErr_SetString(PyExc_ValueError, "Set credentials first.");
		return NULL;
	}

	if (pam_authenticate(tconv->pamh, flags) == PAM_SUCCESS) {
		if (pam_acct_mgmt(tconv->pamh, flags) == PAM_SUCCESS) {
			Py_RETURN_TRUE;
		} else {
			PyErr_SetString(PyExc_RuntimeError,
				"PAM failure in pam_acct_mgmt");
		}
	} else {
		PyErr_SetString(PyExc_RuntimeError,
			"PAM failure in pam_authenticate");
	}

	return NULL;
}

static PyMethodDef spypamMethods[] = {
	{"auth", spypam_authenticate_simple, METH_VARARGS, \
		"Try to authenticate with given credentials."},
	{"_pam_start", spypam_pam_start, METH_VARARGS, \
		"(Internal) Open a PAM handle and return pointer."},
	{"_pam_end", spypam_pam_end, METH_VARARGS, \
		"(Internal) Close a PAM handle and free pointer."},
	{"_pam_session_open", spypam_session_open, METH_VARARGS, \
		"(Internal) Open a new PAM \"session\"."},
	{"_pam_session_close", spypam_session_close, METH_VARARGS, \
		"(Internal) Close an open PAM \"session\"."},
	{"_pam_set_creds", spypam_set_creds, METH_VARARGS, \
		"(Internal) Set conversational credentials."},
	{"_pam_auth", spypam_authenticate, METH_VARARGS, \
		"(Internal) Authenticate with credentials from _pam_set_creds"},
	{NULL}
};

PyMODINIT_FUNC init_spypam(void) {
	PyObject* m = Py_InitModule3("_spypam", spypamMethods,
		"Simple Python PAM module (internal functions)");
}

/* vim: ts=4 noexpandtab
 */
