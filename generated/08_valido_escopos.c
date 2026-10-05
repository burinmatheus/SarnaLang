#include <stdio.h>
#include <string.h>

int main(void) {
    int sl_1_x = 5;
    char sl_2_nome[256] = "";
    strncpy(sl_2_nome, "externo", sizeof(sl_2_nome) - 1);
    sl_2_nome[sizeof(sl_2_nome) - 1] = '\0';
    if (1) {
        int sl_3_x = (sl_1_x + 1);
        char sl_4_nome[256] = "";
        strncpy(sl_4_nome, sl_2_nome, sizeof(sl_4_nome) - 1);
        sl_4_nome[sizeof(sl_4_nome) - 1] = '\0';
        printf("%d", sl_3_x);
        printf(" ");
        printf("%s", sl_4_nome);
        printf("\n");
        scanf("%d", &sl_3_x);
        printf("%d", sl_3_x);
        printf("\n");
        if (1) {
            int sl_5_nome = (strcmp(sl_4_nome, "externo") == 0);
            printf("%s", (sl_5_nome) ? "SHOW" : "NAO SHOW");
            printf("\n");
        }
    }
    printf("%d", sl_1_x);
    printf(" ");
    printf("%s", sl_2_nome);
    printf("\n");
    return 0;
}
