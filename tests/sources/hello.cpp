#include <cstdio>

int main(int argc, char* argv[]) {
    printf("hello from cpp!\n");
    for (int i = 0; i < argc; i++) {
        printf("param %d: %s\n", i, argv[i]);
    }

    return 0;
}