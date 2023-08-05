/*  Setuptools Script Launcher for Windows

    This is a stub executable for Windows that functions somewhat like
    Effbot's "exemaker", in that it runs a script with the same name but
    a .py extension, using information from a #! line.  It differs in that
    it spawns the actual Python executable, rather than attempting to
    hook into the Python DLL.  This means that the script will run with
    sys.executable set to the Python executable, where exemaker ends up with
    sys.executable pointing to itself.  (Which means it won't work if you try
    to run another Python process using sys.executable.)

    To build/rebuild with mingw32, do this in the setuptools project directory:

       gcc -DGUI=0           -mno-cygwin -O -s -o setuptools/cli.exe launcher.c
       gcc -DGUI=1 -mwindows -mno-cygwin -O -s -o setuptools/gui.exe launcher.c

    It links to msvcrt.dll, but this shouldn't be a problem since it doesn't
    actually run Python in the same process.  Note that using 'exec' instead
    of 'spawn' doesn't work, because on Windows this leads to the Python
    executable running in the *background*, attached to the same console
    window, meaning you get a command prompt back *before* Python even finishes
    starting.  So, we have to use spawnv() and wait for Python to exit before
    continuing.  :(
*/
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include "windows.h"

int fail(char *format, char *data) {
    /* Print error message to stderr and return 1 */
    fprintf(stderr, format, data);
    return 2;
}
char *quoted(char *data) {
    char *result = calloc(strlen(data)+3,sizeof(char));
    strcat(result,"\""); strcat(result,data); strcat(result,"\"");
    return result;
}

int run(int argc, char **argv, int is_gui) {

    char python[256];   /* python executable's filename*/
    char script[256];   /* the script's filename */

    HINSTANCE hPython;  /* DLL handle for python executable */
    int scriptf;        /* file descriptor for script file */

    char **newargs;     /* argument array for exec */
    char *ptr, *end;    /* working pointers for string manipulation */

    /* compute script name from our .exe name*/
    GetModuleFileName(NULL, script, sizeof(script));
    end = script + strlen(script);
    while( end>script && *end != '.')
        *end-- = '\0';
    *end-- = '\0';
    strcat(script, (GUI ? "-script.pyw" : "-script.py"));

    /* figure out the target python executable */

    scriptf = open(script, O_RDONLY);
    if (scriptf == -1) {
        return fail("Cannot open %s\n", script);
    }
    end = python + read(scriptf, python, sizeof(python));
    close(scriptf);

    ptr = python-1;
    while(++ptr < end && *ptr && *ptr!='\n' && *ptr!='\r') {
        if (*ptr=='/')
            *ptr='\\';  /* convert slashes to avoid LoadLibrary crashes... */
    }

    *ptr = '\0';
    while (ptr>python && isspace(*ptr)) *ptr-- = '\0';  /* strip trailing sp */
    if (strncmp(python, "#!", 2)) {
        /* default to python.exe if no #! header */
        strcpy(python, "#!python.exe");
    }

    /* At this point, the python buffer contains "#!pythonfilename" */

    /* Using spawnv() can fail strangely if you e.g. find the Cygwin
       Python, so we'll make sure Windows can find and load it */
    hPython = LoadLibraryEx(python+2, NULL, LOAD_WITH_ALTERED_SEARCH_PATH);
    if (!hPython) {
        return fail("Cannot find Python executable %s\n", python+2);
    }

    /* And we'll use the absolute filename for spawnv */
    GetModuleFileName(hPython, python, sizeof(python));

    /* printf("Python executable: %s\n", python); */

    /* Argument array needs to be argc+1 for args, plus 1 for null sentinel */
    newargs = (char **)calloc(argc+2, sizeof(char *));
    newargs[0] = quoted(python);
    newargs[1] = quoted(script);
    memcpy(newargs+2, argv+1, (argc-1)*sizeof(char *));
    newargs[argc+1] = NULL;

    /* printf("args 0: %s\nargs 1: %s\n", newargs[0], newargs[1]); */
    if (is_gui) {
        /* Use exec, we don't need to wait for the GUI to finish */
        execv(python, (const char * const *)(newargs));
        return fail("Could not exec %s", python);   /* shouldn't get here! */
    }
    /* We *do* need to wait for a CLI to finish, so use spawn */
    return spawnv(P_WAIT, python, (const char * const *)(newargs));
}


int WINAPI WinMain(HINSTANCE hI, HINSTANCE hP, LPSTR lpCmd, int nShow) {
    return run(__argc, __argv, GUI);
}






