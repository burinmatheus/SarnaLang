#include <stdio.h>
#include <string.h>

int main(void) {
    int sl_1_portao = 10;
    double sl_2_tamanho_casona = 2.5;
    sl_1_portao = (sl_1_portao + 5);
    printf("%s", "Portão:");
    printf(" ");
    printf("%d", sl_1_portao);
    printf("\n");
    printf("%s", "Casona:");
    printf(" ");
    printf("%g", sl_2_tamanho_casona);
    printf("\n");
    return 0;
}
