#include <stdio.h>
#include <string.h>

int main(void) {
    int sl_1_numero_portao = 12;
    double sl_2_tamanho_casa = 3.5;
    char sl_3_apelido[256] = "";
    strncpy(sl_3_apelido, "Marcelo", sizeof(sl_3_apelido) - 1);
    sl_3_apelido[sizeof(sl_3_apelido) - 1] = '\0';
    int sl_4_graxa_veia = 1;
    if (((sl_1_numero_portao > 10) && (sl_4_graxa_veia == 1))) {
        printf("%s", "Mas tu é sarna né,");
        printf(" ");
        printf("%s", sl_3_apelido);
        printf(" ");
        printf("%s", "- o portãozão é");
        printf(" ");
        printf("%d", sl_1_numero_portao);
        printf("\n");
    } else {
        printf("%s", "Não é sarna não.");
        printf("\n");
    }
    while ((sl_1_numero_portao > 9)) {
        printf("%s", "Portãozão:");
        printf(" ");
        printf("%d", sl_1_numero_portao);
        printf("\n");
        sl_1_numero_portao = (sl_1_numero_portao - 1);
    }
    printf("%s", "SHOW DE BOLA!");
    printf("\n");
    return 0;
}
