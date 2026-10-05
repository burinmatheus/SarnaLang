#include <stdio.h>
#include <string.h>

int main(void) {
    int sl_1_repeticoes = 3;
    double sl_2_carga = 10.5;
    int sl_3_precedencia = (2 + (3 * 4));
    char sl_4_nome[256] = "";
    strncpy(sl_4_nome, "", sizeof(sl_4_nome) - 1);
    sl_4_nome[sizeof(sl_4_nome) - 1] = '\0';
    int sl_5_autorizado = 1;
    printf("%s", "Qual teu nome?");
    printf("\n");
    scanf("%255s", sl_4_nome);
    while ((sl_1_repeticoes > 0)) {
        printf("%s", "Repetição:");
        printf(" ");
        printf("%d", sl_1_repeticoes);
        printf("\n");
        sl_2_carga = (sl_2_carga + (2 * 1.5));
        sl_1_repeticoes = (sl_1_repeticoes - 1);
    }
    if (((sl_2_carga >= 15) && (sl_5_autorizado == 1))) {
        printf("%s", "Show de bola,");
        printf(" ");
        printf("%s", sl_4_nome);
        printf("\n");
    } else {
        printf("%s", "Ainda falta carga.");
        printf("\n");
    }
    printf("%s", "2 + 3 * 4 =");
    printf(" ");
    printf("%d", sl_3_precedencia);
    printf("\n");
    return 0;
}
