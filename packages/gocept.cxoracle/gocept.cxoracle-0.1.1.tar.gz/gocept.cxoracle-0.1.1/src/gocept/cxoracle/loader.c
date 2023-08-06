/* load python with set envvars */

#include <stdlib.h>
#include <sys/utsname.h>
#include <unistd.h>
#include <stdio.h>

int main(int argc, char* argv[]) {

    struct utsname uinfo;
    char *varname;

    uname(&uinfo);
    if (strcmp(uinfo.sysname, "Darwin") == 0) {
        varname = "DYLD_LIBRARY_PATH";
    } else {
        varname = "LD_LIBRARY_PATH";
    }
    setenv(varname, ORACLE_HOME, 1);
    setenv("ORACLE_HOME", ORACLE_HOME, 1);

    execvp(PYTHON_EXECUTABLE, argv);
}
