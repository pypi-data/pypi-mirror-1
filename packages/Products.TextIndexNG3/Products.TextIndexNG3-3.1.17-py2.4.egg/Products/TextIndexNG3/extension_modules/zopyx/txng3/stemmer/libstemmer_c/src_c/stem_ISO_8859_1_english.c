
/* This file was generated automatically by the Snowball to ANSI C compiler */

#include "../runtime/header.h"

extern int english_ISO_8859_1_stem(struct SN_env * z);
static int r_exception2(struct SN_env * z);
static int r_exception1(struct SN_env * z);
static int r_Step_5(struct SN_env * z);
static int r_Step_4(struct SN_env * z);
static int r_Step_3(struct SN_env * z);
static int r_Step_2(struct SN_env * z);
static int r_Step_1c(struct SN_env * z);
static int r_Step_1b(struct SN_env * z);
static int r_Step_1a(struct SN_env * z);
static int r_R2(struct SN_env * z);
static int r_R1(struct SN_env * z);
static int r_shortv(struct SN_env * z);
static int r_mark_regions(struct SN_env * z);
static int r_postlude(struct SN_env * z);
static int r_prelude(struct SN_env * z);

extern struct SN_env * english_ISO_8859_1_create_env(void);
extern void english_ISO_8859_1_close_env(struct SN_env * z);

static symbol s_0_0[6] = { 'c', 'o', 'm', 'm', 'u', 'n' };
static symbol s_0_1[5] = { 'g', 'e', 'n', 'e', 'r' };

static struct among a_0[2] =
{
/*  0 */ { 6, s_0_0, -1, -1, 0},
/*  1 */ { 5, s_0_1, -1, -1, 0}
};

static symbol s_1_0[3] = { 'i', 'e', 'd' };
static symbol s_1_1[1] = { 's' };
static symbol s_1_2[3] = { 'i', 'e', 's' };
static symbol s_1_3[4] = { 's', 's', 'e', 's' };
static symbol s_1_4[2] = { 's', 's' };
static symbol s_1_5[2] = { 'u', 's' };

static struct among a_1[6] =
{
/*  0 */ { 3, s_1_0, -1, 2, 0},
/*  1 */ { 1, s_1_1, -1, 3, 0},
/*  2 */ { 3, s_1_2, 1, 2, 0},
/*  3 */ { 4, s_1_3, 1, 1, 0},
/*  4 */ { 2, s_1_4, 1, -1, 0},
/*  5 */ { 2, s_1_5, 1, -1, 0}
};

static symbol s_2_1[2] = { 'b', 'b' };
static symbol s_2_2[2] = { 'd', 'd' };
static symbol s_2_3[2] = { 'f', 'f' };
static symbol s_2_4[2] = { 'g', 'g' };
static symbol s_2_5[2] = { 'b', 'l' };
static symbol s_2_6[2] = { 'm', 'm' };
static symbol s_2_7[2] = { 'n', 'n' };
static symbol s_2_8[2] = { 'p', 'p' };
static symbol s_2_9[2] = { 'r', 'r' };
static symbol s_2_10[2] = { 'a', 't' };
static symbol s_2_11[2] = { 't', 't' };
static symbol s_2_12[2] = { 'i', 'z' };

static struct among a_2[13] =
{
/*  0 */ { 0, 0, -1, 3, 0},
/*  1 */ { 2, s_2_1, 0, 2, 0},
/*  2 */ { 2, s_2_2, 0, 2, 0},
/*  3 */ { 2, s_2_3, 0, 2, 0},
/*  4 */ { 2, s_2_4, 0, 2, 0},
/*  5 */ { 2, s_2_5, 0, 1, 0},
/*  6 */ { 2, s_2_6, 0, 2, 0},
/*  7 */ { 2, s_2_7, 0, 2, 0},
/*  8 */ { 2, s_2_8, 0, 2, 0},
/*  9 */ { 2, s_2_9, 0, 2, 0},
/* 10 */ { 2, s_2_10, 0, 1, 0},
/* 11 */ { 2, s_2_11, 0, 2, 0},
/* 12 */ { 2, s_2_12, 0, 1, 0}
};

static symbol s_3_0[2] = { 'e', 'd' };
static symbol s_3_1[3] = { 'e', 'e', 'd' };
static symbol s_3_2[3] = { 'i', 'n', 'g' };
static symbol s_3_3[4] = { 'e', 'd', 'l', 'y' };
static symbol s_3_4[5] = { 'e', 'e', 'd', 'l', 'y' };
static symbol s_3_5[5] = { 'i', 'n', 'g', 'l', 'y' };

static struct among a_3[6] =
{
/*  0 */ { 2, s_3_0, -1, 2, 0},
/*  1 */ { 3, s_3_1, 0, 1, 0},
/*  2 */ { 3, s_3_2, -1, 2, 0},
/*  3 */ { 4, s_3_3, -1, 2, 0},
/*  4 */ { 5, s_3_4, 3, 1, 0},
/*  5 */ { 5, s_3_5, -1, 2, 0}
};

static symbol s_4_0[4] = { 'a', 'n', 'c', 'i' };
static symbol s_4_1[4] = { 'e', 'n', 'c', 'i' };
static symbol s_4_2[3] = { 'o', 'g', 'i' };
static symbol s_4_3[2] = { 'l', 'i' };
static symbol s_4_4[3] = { 'b', 'l', 'i' };
static symbol s_4_5[4] = { 'a', 'b', 'l', 'i' };
static symbol s_4_6[4] = { 'a', 'l', 'l', 'i' };
static symbol s_4_7[5] = { 'f', 'u', 'l', 'l', 'i' };
static symbol s_4_8[6] = { 'l', 'e', 's', 's', 'l', 'i' };
static symbol s_4_9[5] = { 'o', 'u', 's', 'l', 'i' };
static symbol s_4_10[5] = { 'e', 'n', 't', 'l', 'i' };
static symbol s_4_11[5] = { 'a', 'l', 'i', 't', 'i' };
static symbol s_4_12[6] = { 'b', 'i', 'l', 'i', 't', 'i' };
static symbol s_4_13[5] = { 'i', 'v', 'i', 't', 'i' };
static symbol s_4_14[6] = { 't', 'i', 'o', 'n', 'a', 'l' };
static symbol s_4_15[7] = { 'a', 't', 'i', 'o', 'n', 'a', 'l' };
static symbol s_4_16[5] = { 'a', 'l', 'i', 's', 'm' };
static symbol s_4_17[5] = { 'a', 't', 'i', 'o', 'n' };
static symbol s_4_18[7] = { 'i', 'z', 'a', 't', 'i', 'o', 'n' };
static symbol s_4_19[4] = { 'i', 'z', 'e', 'r' };
static symbol s_4_20[4] = { 'a', 't', 'o', 'r' };
static symbol s_4_21[7] = { 'i', 'v', 'e', 'n', 'e', 's', 's' };
static symbol s_4_22[7] = { 'f', 'u', 'l', 'n', 'e', 's', 's' };
static symbol s_4_23[7] = { 'o', 'u', 's', 'n', 'e', 's', 's' };

static struct among a_4[24] =
{
/*  0 */ { 4, s_4_0, -1, 3, 0},
/*  1 */ { 4, s_4_1, -1, 2, 0},
/*  2 */ { 3, s_4_2, -1, 13, 0},
/*  3 */ { 2, s_4_3, -1, 16, 0},
/*  4 */ { 3, s_4_4, 3, 12, 0},
/*  5 */ { 4, s_4_5, 4, 4, 0},
/*  6 */ { 4, s_4_6, 3, 8, 0},
/*  7 */ { 5, s_4_7, 3, 14, 0},
/*  8 */ { 6, s_4_8, 3, 15, 0},
/*  9 */ { 5, s_4_9, 3, 10, 0},
/* 10 */ { 5, s_4_10, 3, 5, 0},
/* 11 */ { 5, s_4_11, -1, 8, 0},
/* 12 */ { 6, s_4_12, -1, 12, 0},
/* 13 */ { 5, s_4_13, -1, 11, 0},
/* 14 */ { 6, s_4_14, -1, 1, 0},
/* 15 */ { 7, s_4_15, 14, 7, 0},
/* 16 */ { 5, s_4_16, -1, 8, 0},
/* 17 */ { 5, s_4_17, -1, 7, 0},
/* 18 */ { 7, s_4_18, 17, 6, 0},
/* 19 */ { 4, s_4_19, -1, 6, 0},
/* 20 */ { 4, s_4_20, -1, 7, 0},
/* 21 */ { 7, s_4_21, -1, 11, 0},
/* 22 */ { 7, s_4_22, -1, 9, 0},
/* 23 */ { 7, s_4_23, -1, 10, 0}
};

static symbol s_5_0[5] = { 'i', 'c', 'a', 't', 'e' };
static symbol s_5_1[5] = { 'a', 't', 'i', 'v', 'e' };
static symbol s_5_2[5] = { 'a', 'l', 'i', 'z', 'e' };
static symbol s_5_3[5] = { 'i', 'c', 'i', 't', 'i' };
static symbol s_5_4[4] = { 'i', 'c', 'a', 'l' };
static symbol s_5_5[6] = { 't', 'i', 'o', 'n', 'a', 'l' };
static symbol s_5_6[7] = { 'a', 't', 'i', 'o', 'n', 'a', 'l' };
static symbol s_5_7[3] = { 'f', 'u', 'l' };
static symbol s_5_8[4] = { 'n', 'e', 's', 's' };

static struct among a_5[9] =
{
/*  0 */ { 5, s_5_0, -1, 4, 0},
/*  1 */ { 5, s_5_1, -1, 6, 0},
/*  2 */ { 5, s_5_2, -1, 3, 0},
/*  3 */ { 5, s_5_3, -1, 4, 0},
/*  4 */ { 4, s_5_4, -1, 4, 0},
/*  5 */ { 6, s_5_5, -1, 1, 0},
/*  6 */ { 7, s_5_6, 5, 2, 0},
/*  7 */ { 3, s_5_7, -1, 5, 0},
/*  8 */ { 4, s_5_8, -1, 5, 0}
};

static symbol s_6_0[2] = { 'i', 'c' };
static symbol s_6_1[4] = { 'a', 'n', 'c', 'e' };
static symbol s_6_2[4] = { 'e', 'n', 'c', 'e' };
static symbol s_6_3[4] = { 'a', 'b', 'l', 'e' };
static symbol s_6_4[4] = { 'i', 'b', 'l', 'e' };
static symbol s_6_5[3] = { 'a', 't', 'e' };
static symbol s_6_6[3] = { 'i', 'v', 'e' };
static symbol s_6_7[3] = { 'i', 'z', 'e' };
static symbol s_6_8[3] = { 'i', 't', 'i' };
static symbol s_6_9[2] = { 'a', 'l' };
static symbol s_6_10[3] = { 'i', 's', 'm' };
static symbol s_6_11[3] = { 'i', 'o', 'n' };
static symbol s_6_12[2] = { 'e', 'r' };
static symbol s_6_13[3] = { 'o', 'u', 's' };
static symbol s_6_14[3] = { 'a', 'n', 't' };
static symbol s_6_15[3] = { 'e', 'n', 't' };
static symbol s_6_16[4] = { 'm', 'e', 'n', 't' };
static symbol s_6_17[5] = { 'e', 'm', 'e', 'n', 't' };

static struct among a_6[18] =
{
/*  0 */ { 2, s_6_0, -1, 1, 0},
/*  1 */ { 4, s_6_1, -1, 1, 0},
/*  2 */ { 4, s_6_2, -1, 1, 0},
/*  3 */ { 4, s_6_3, -1, 1, 0},
/*  4 */ { 4, s_6_4, -1, 1, 0},
/*  5 */ { 3, s_6_5, -1, 1, 0},
/*  6 */ { 3, s_6_6, -1, 1, 0},
/*  7 */ { 3, s_6_7, -1, 1, 0},
/*  8 */ { 3, s_6_8, -1, 1, 0},
/*  9 */ { 2, s_6_9, -1, 1, 0},
/* 10 */ { 3, s_6_10, -1, 1, 0},
/* 11 */ { 3, s_6_11, -1, 2, 0},
/* 12 */ { 2, s_6_12, -1, 1, 0},
/* 13 */ { 3, s_6_13, -1, 1, 0},
/* 14 */ { 3, s_6_14, -1, 1, 0},
/* 15 */ { 3, s_6_15, -1, 1, 0},
/* 16 */ { 4, s_6_16, 15, 1, 0},
/* 17 */ { 5, s_6_17, 16, 1, 0}
};

static symbol s_7_0[1] = { 'e' };
static symbol s_7_1[1] = { 'l' };

static struct among a_7[2] =
{
/*  0 */ { 1, s_7_0, -1, 1, 0},
/*  1 */ { 1, s_7_1, -1, 2, 0}
};

static symbol s_8_0[7] = { 's', 'u', 'c', 'c', 'e', 'e', 'd' };
static symbol s_8_1[7] = { 'p', 'r', 'o', 'c', 'e', 'e', 'd' };
static symbol s_8_2[6] = { 'e', 'x', 'c', 'e', 'e', 'd' };
static symbol s_8_3[7] = { 'c', 'a', 'n', 'n', 'i', 'n', 'g' };
static symbol s_8_4[6] = { 'i', 'n', 'n', 'i', 'n', 'g' };
static symbol s_8_5[7] = { 'e', 'a', 'r', 'r', 'i', 'n', 'g' };
static symbol s_8_6[7] = { 'h', 'e', 'r', 'r', 'i', 'n', 'g' };
static symbol s_8_7[6] = { 'o', 'u', 't', 'i', 'n', 'g' };

static struct among a_8[8] =
{
/*  0 */ { 7, s_8_0, -1, -1, 0},
/*  1 */ { 7, s_8_1, -1, -1, 0},
/*  2 */ { 6, s_8_2, -1, -1, 0},
/*  3 */ { 7, s_8_3, -1, -1, 0},
/*  4 */ { 6, s_8_4, -1, -1, 0},
/*  5 */ { 7, s_8_5, -1, -1, 0},
/*  6 */ { 7, s_8_6, -1, -1, 0},
/*  7 */ { 6, s_8_7, -1, -1, 0}
};

static symbol s_9_0[5] = { 'a', 'n', 'd', 'e', 's' };
static symbol s_9_1[5] = { 'a', 't', 'l', 'a', 's' };
static symbol s_9_2[4] = { 'b', 'i', 'a', 's' };
static symbol s_9_3[6] = { 'c', 'o', 's', 'm', 'o', 's' };
static symbol s_9_4[5] = { 'd', 'y', 'i', 'n', 'g' };
static symbol s_9_5[5] = { 'e', 'a', 'r', 'l', 'y' };
static symbol s_9_6[6] = { 'g', 'e', 'n', 't', 'l', 'y' };
static symbol s_9_7[4] = { 'h', 'o', 'w', 'e' };
static symbol s_9_8[4] = { 'i', 'd', 'l', 'y' };
static symbol s_9_9[5] = { 'l', 'y', 'i', 'n', 'g' };
static symbol s_9_10[4] = { 'n', 'e', 'w', 's' };
static symbol s_9_11[4] = { 'o', 'n', 'l', 'y' };
static symbol s_9_12[6] = { 's', 'i', 'n', 'g', 'l', 'y' };
static symbol s_9_13[5] = { 's', 'k', 'i', 'e', 's' };
static symbol s_9_14[4] = { 's', 'k', 'i', 's' };
static symbol s_9_15[3] = { 's', 'k', 'y' };
static symbol s_9_16[5] = { 't', 'y', 'i', 'n', 'g' };
static symbol s_9_17[4] = { 'u', 'g', 'l', 'y' };

static struct among a_9[18] =
{
/*  0 */ { 5, s_9_0, -1, -1, 0},
/*  1 */ { 5, s_9_1, -1, -1, 0},
/*  2 */ { 4, s_9_2, -1, -1, 0},
/*  3 */ { 6, s_9_3, -1, -1, 0},
/*  4 */ { 5, s_9_4, -1, 3, 0},
/*  5 */ { 5, s_9_5, -1, 9, 0},
/*  6 */ { 6, s_9_6, -1, 7, 0},
/*  7 */ { 4, s_9_7, -1, -1, 0},
/*  8 */ { 4, s_9_8, -1, 6, 0},
/*  9 */ { 5, s_9_9, -1, 4, 0},
/* 10 */ { 4, s_9_10, -1, -1, 0},
/* 11 */ { 4, s_9_11, -1, 10, 0},
/* 12 */ { 6, s_9_12, -1, 11, 0},
/* 13 */ { 5, s_9_13, -1, 2, 0},
/* 14 */ { 4, s_9_14, -1, 1, 0},
/* 15 */ { 3, s_9_15, -1, -1, 0},
/* 16 */ { 5, s_9_16, -1, 5, 0},
/* 17 */ { 4, s_9_17, -1, 8, 0}
};

static unsigned char g_v[] = { 17, 65, 16, 1 };

static unsigned char g_v_WXY[] = { 1, 17, 65, 208, 1 };

static unsigned char g_valid_LI[] = { 55, 141, 2 };

static symbol s_0[] = { 'y' };
static symbol s_1[] = { 'Y' };
static symbol s_2[] = { 'y' };
static symbol s_3[] = { 'Y' };
static symbol s_4[] = { 's', 's' };
static symbol s_5[] = { 'i', 'e' };
static symbol s_6[] = { 'i' };
static symbol s_7[] = { 'e', 'e' };
static symbol s_8[] = { 'e' };
static symbol s_9[] = { 'e' };
static symbol s_10[] = { 'y' };
static symbol s_11[] = { 'Y' };
static symbol s_12[] = { 'i' };
static symbol s_13[] = { 't', 'i', 'o', 'n' };
static symbol s_14[] = { 'e', 'n', 'c', 'e' };
static symbol s_15[] = { 'a', 'n', 'c', 'e' };
static symbol s_16[] = { 'a', 'b', 'l', 'e' };
static symbol s_17[] = { 'e', 'n', 't' };
static symbol s_18[] = { 'i', 'z', 'e' };
static symbol s_19[] = { 'a', 't', 'e' };
static symbol s_20[] = { 'a', 'l' };
static symbol s_21[] = { 'f', 'u', 'l' };
static symbol s_22[] = { 'o', 'u', 's' };
static symbol s_23[] = { 'i', 'v', 'e' };
static symbol s_24[] = { 'b', 'l', 'e' };
static symbol s_25[] = { 'l' };
static symbol s_26[] = { 'o', 'g' };
static symbol s_27[] = { 'f', 'u', 'l' };
static symbol s_28[] = { 'l', 'e', 's', 's' };
static symbol s_29[] = { 't', 'i', 'o', 'n' };
static symbol s_30[] = { 'a', 't', 'e' };
static symbol s_31[] = { 'a', 'l' };
static symbol s_32[] = { 'i', 'c' };
static symbol s_33[] = { 's' };
static symbol s_34[] = { 't' };
static symbol s_35[] = { 'l' };
static symbol s_36[] = { 's', 'k', 'i' };
static symbol s_37[] = { 's', 'k', 'y' };
static symbol s_38[] = { 'd', 'i', 'e' };
static symbol s_39[] = { 'l', 'i', 'e' };
static symbol s_40[] = { 't', 'i', 'e' };
static symbol s_41[] = { 'i', 'd', 'l' };
static symbol s_42[] = { 'g', 'e', 'n', 't', 'l' };
static symbol s_43[] = { 'u', 'g', 'l', 'i' };
static symbol s_44[] = { 'e', 'a', 'r', 'l', 'i' };
static symbol s_45[] = { 'o', 'n', 'l', 'i' };
static symbol s_46[] = { 's', 'i', 'n', 'g', 'l' };
static symbol s_47[] = { 'Y' };
static symbol s_48[] = { 'y' };

static int r_prelude(struct SN_env * z) {
    z->B[0] = 0; /* unset Y_found, line 24 */
    {   int c = z->c; /* do, line 25 */
        z->bra = z->c; /* [, line 25 */
        if (!(eq_s(z, 1, s_0))) goto lab0;
        z->ket = z->c; /* ], line 25 */
        if (!(in_grouping(z, g_v, 97, 121))) goto lab0;
        {   int ret;
            ret = slice_from_s(z, 1, s_1); /* <-, line 25 */
            if (ret < 0) return ret;
        }
        z->B[0] = 1; /* set Y_found, line 25 */
    lab0:
        z->c = c;
    }
    {   int c = z->c; /* do, line 26 */
        while(1) { /* repeat, line 26 */
            int c = z->c;
            while(1) { /* goto, line 26 */
                int c = z->c;
                if (!(in_grouping(z, g_v, 97, 121))) goto lab3;
                z->bra = z->c; /* [, line 26 */
                if (!(eq_s(z, 1, s_2))) goto lab3;
                z->ket = z->c; /* ], line 26 */
                z->c = c;
                break;
            lab3:
                z->c = c;
                if (z->c >= z->l) goto lab2;
                z->c++; /* goto, line 26 */
            }
            {   int ret;
                ret = slice_from_s(z, 1, s_3); /* <-, line 26 */
                if (ret < 0) return ret;
            }
            z->B[0] = 1; /* set Y_found, line 26 */
            continue;
        lab2:
            z->c = c;
            break;
        }
        z->c = c;
    }
    return 1;
}

static int r_mark_regions(struct SN_env * z) {
    z->I[0] = z->l;
    z->I[1] = z->l;
    {   int c = z->c; /* do, line 32 */
        {   int c = z->c; /* or, line 37 */
            if (!(find_among(z, a_0, 2))) goto lab2; /* among, line 33 */
            goto lab1;
        lab2:
            z->c = c;
            while(1) { /* gopast, line 37 */
                if (!(in_grouping(z, g_v, 97, 121))) goto lab3;
                break;
            lab3:
                if (z->c >= z->l) goto lab0;
                z->c++; /* gopast, line 37 */
            }
            while(1) { /* gopast, line 37 */
                if (!(out_grouping(z, g_v, 97, 121))) goto lab4;
                break;
            lab4:
                if (z->c >= z->l) goto lab0;
                z->c++; /* gopast, line 37 */
            }
        }
    lab1:
        z->I[0] = z->c; /* setmark p1, line 38 */
        while(1) { /* gopast, line 39 */
            if (!(in_grouping(z, g_v, 97, 121))) goto lab5;
            break;
        lab5:
            if (z->c >= z->l) goto lab0;
            z->c++; /* gopast, line 39 */
        }
        while(1) { /* gopast, line 39 */
            if (!(out_grouping(z, g_v, 97, 121))) goto lab6;
            break;
        lab6:
            if (z->c >= z->l) goto lab0;
            z->c++; /* gopast, line 39 */
        }
        z->I[1] = z->c; /* setmark p2, line 39 */
    lab0:
        z->c = c;
    }
    return 1;
}

static int r_shortv(struct SN_env * z) {
    {   int m = z->l - z->c; (void) m; /* or, line 47 */
        if (!(out_grouping_b(z, g_v_WXY, 89, 121))) goto lab1;
        if (!(in_grouping_b(z, g_v, 97, 121))) goto lab1;
        if (!(out_grouping_b(z, g_v, 97, 121))) goto lab1;
        goto lab0;
    lab1:
        z->c = z->l - m;
        if (!(out_grouping_b(z, g_v, 97, 121))) return 0;
        if (!(in_grouping_b(z, g_v, 97, 121))) return 0;
        if (z->c > z->lb) return 0; /* atlimit, line 48 */
    }
lab0:
    return 1;
}

static int r_R1(struct SN_env * z) {
    if (!(z->I[0] <= z->c)) return 0;
    return 1;
}

static int r_R2(struct SN_env * z) {
    if (!(z->I[1] <= z->c)) return 0;
    return 1;
}

static int r_Step_1a(struct SN_env * z) {
    int among_var;
    z->ket = z->c; /* [, line 55 */
    among_var = find_among_b(z, a_1, 6); /* substring, line 55 */
    if (!(among_var)) return 0;
    z->bra = z->c; /* ], line 55 */
    switch(among_var) {
        case 0: return 0;
        case 1:
            {   int ret;
                ret = slice_from_s(z, 2, s_4); /* <-, line 56 */
                if (ret < 0) return ret;
            }
            break;
        case 2:
            {   int m = z->l - z->c; (void) m; /* or, line 58 */
                if (z->c <= z->lb) goto lab1;
                z->c--; /* next, line 58 */
                if (z->c > z->lb) goto lab1; /* atlimit, line 58 */
                {   int ret;
                    ret = slice_from_s(z, 2, s_5); /* <-, line 58 */
                    if (ret < 0) return ret;
                }
                goto lab0;
            lab1:
                z->c = z->l - m;
                {   int ret;
                    ret = slice_from_s(z, 1, s_6); /* <-, line 58 */
                    if (ret < 0) return ret;
                }
            }
        lab0:
            break;
        case 3:
            if (z->c <= z->lb) return 0;
            z->c--; /* next, line 59 */
            while(1) { /* gopast, line 59 */
                if (!(in_grouping_b(z, g_v, 97, 121))) goto lab2;
                break;
            lab2:
                if (z->c <= z->lb) return 0;
                z->c--; /* gopast, line 59 */
            }
            {   int ret;
                ret = slice_del(z); /* delete, line 59 */
                if (ret < 0) return ret;
            }
            break;
    }
    return 1;
}

static int r_Step_1b(struct SN_env * z) {
    int among_var;
    z->ket = z->c; /* [, line 65 */
    among_var = find_among_b(z, a_3, 6); /* substring, line 65 */
    if (!(among_var)) return 0;
    z->bra = z->c; /* ], line 65 */
    switch(among_var) {
        case 0: return 0;
        case 1:
            {   int ret = r_R1(z);
                if (ret == 0) return 0; /* call R1, line 67 */
                if (ret < 0) return ret;
            }
            {   int ret;
                ret = slice_from_s(z, 2, s_7); /* <-, line 67 */
                if (ret < 0) return ret;
            }
            break;
        case 2:
            {   int m_test = z->l - z->c; /* test, line 70 */
                while(1) { /* gopast, line 70 */
                    if (!(in_grouping_b(z, g_v, 97, 121))) goto lab0;
                    break;
                lab0:
                    if (z->c <= z->lb) return 0;
                    z->c--; /* gopast, line 70 */
                }
                z->c = z->l - m_test;
            }
            {   int ret;
                ret = slice_del(z); /* delete, line 70 */
                if (ret < 0) return ret;
            }
            {   int m_test = z->l - z->c; /* test, line 71 */
                among_var = find_among_b(z, a_2, 13); /* substring, line 71 */
                if (!(among_var)) return 0;
                z->c = z->l - m_test;
            }
            switch(among_var) {
                case 0: return 0;
                case 1:
                    {   int ret;
                        {   int c = z->c;
                            ret = insert_s(z, z->c, z->c, 1, s_8); /* <+, line 73 */
                            z->c = c;
                        }
                        if (ret < 0) return ret;
                    }
                    break;
                case 2:
                    z->ket = z->c; /* [, line 76 */
                    if (z->c <= z->lb) return 0;
                    z->c--; /* next, line 76 */
                    z->bra = z->c; /* ], line 76 */
                    {   int ret;
                        ret = slice_del(z); /* delete, line 76 */
                        if (ret < 0) return ret;
                    }
                    break;
                case 3:
                    if (z->c != z->I[0]) return 0; /* atmark, line 77 */
                    {   int m_test = z->l - z->c; /* test, line 77 */
                        {   int ret = r_shortv(z);
                            if (ret == 0) return 0; /* call shortv, line 77 */
                            if (ret < 0) return ret;
                        }
                        z->c = z->l - m_test;
                    }
                    {   int ret;
                        {   int c = z->c;
                            ret = insert_s(z, z->c, z->c, 1, s_9); /* <+, line 77 */
                            z->c = c;
                        }
                        if (ret < 0) return ret;
                    }
                    break;
            }
            break;
    }
    return 1;
}

static int r_Step_1c(struct SN_env * z) {
    z->ket = z->c; /* [, line 84 */
    {   int m = z->l - z->c; (void) m; /* or, line 84 */
        if (!(eq_s_b(z, 1, s_10))) goto lab1;
        goto lab0;
    lab1:
        z->c = z->l - m;
        if (!(eq_s_b(z, 1, s_11))) return 0;
    }
lab0:
    z->bra = z->c; /* ], line 84 */
    if (!(out_grouping_b(z, g_v, 97, 121))) return 0;
    {   int m = z->l - z->c; (void) m; /* not, line 85 */
        if (z->c > z->lb) goto lab2; /* atlimit, line 85 */
        return 0;
    lab2:
        z->c = z->l - m;
    }
    {   int ret;
        ret = slice_from_s(z, 1, s_12); /* <-, line 86 */
        if (ret < 0) return ret;
    }
    return 1;
}

static int r_Step_2(struct SN_env * z) {
    int among_var;
    z->ket = z->c; /* [, line 90 */
    among_var = find_among_b(z, a_4, 24); /* substring, line 90 */
    if (!(among_var)) return 0;
    z->bra = z->c; /* ], line 90 */
    {   int ret = r_R1(z);
        if (ret == 0) return 0; /* call R1, line 90 */
        if (ret < 0) return ret;
    }
    switch(among_var) {
        case 0: return 0;
        case 1:
            {   int ret;
                ret = slice_from_s(z, 4, s_13); /* <-, line 91 */
                if (ret < 0) return ret;
            }
            break;
        case 2:
            {   int ret;
                ret = slice_from_s(z, 4, s_14); /* <-, line 92 */
                if (ret < 0) return ret;
            }
            break;
        case 3:
            {   int ret;
                ret = slice_from_s(z, 4, s_15); /* <-, line 93 */
                if (ret < 0) return ret;
            }
            break;
        case 4:
            {   int ret;
                ret = slice_from_s(z, 4, s_16); /* <-, line 94 */
                if (ret < 0) return ret;
            }
            break;
        case 5:
            {   int ret;
                ret = slice_from_s(z, 3, s_17); /* <-, line 95 */
                if (ret < 0) return ret;
            }
            break;
        case 6:
            {   int ret;
                ret = slice_from_s(z, 3, s_18); /* <-, line 97 */
                if (ret < 0) return ret;
            }
            break;
        case 7:
            {   int ret;
                ret = slice_from_s(z, 3, s_19); /* <-, line 99 */
                if (ret < 0) return ret;
            }
            break;
        case 8:
            {   int ret;
                ret = slice_from_s(z, 2, s_20); /* <-, line 101 */
                if (ret < 0) return ret;
            }
            break;
        case 9:
            {   int ret;
                ret = slice_from_s(z, 3, s_21); /* <-, line 102 */
                if (ret < 0) return ret;
            }
            break;
        case 10:
            {   int ret;
                ret = slice_from_s(z, 3, s_22); /* <-, line 104 */
                if (ret < 0) return ret;
            }
            break;
        case 11:
            {   int ret;
                ret = slice_from_s(z, 3, s_23); /* <-, line 106 */
                if (ret < 0) return ret;
            }
            break;
        case 12:
            {   int ret;
                ret = slice_from_s(z, 3, s_24); /* <-, line 108 */
                if (ret < 0) return ret;
            }
            break;
        case 13:
            if (!(eq_s_b(z, 1, s_25))) return 0;
            {   int ret;
                ret = slice_from_s(z, 2, s_26); /* <-, line 109 */
                if (ret < 0) return ret;
            }
            break;
        case 14:
            {   int ret;
                ret = slice_from_s(z, 3, s_27); /* <-, line 110 */
                if (ret < 0) return ret;
            }
            break;
        case 15:
            {   int ret;
                ret = slice_from_s(z, 4, s_28); /* <-, line 111 */
                if (ret < 0) return ret;
            }
            break;
        case 16:
            if (!(in_grouping_b(z, g_valid_LI, 99, 116))) return 0;
            {   int ret;
                ret = slice_del(z); /* delete, line 112 */
                if (ret < 0) return ret;
            }
            break;
    }
    return 1;
}

static int r_Step_3(struct SN_env * z) {
    int among_var;
    z->ket = z->c; /* [, line 117 */
    among_var = find_among_b(z, a_5, 9); /* substring, line 117 */
    if (!(among_var)) return 0;
    z->bra = z->c; /* ], line 117 */
    {   int ret = r_R1(z);
        if (ret == 0) return 0; /* call R1, line 117 */
        if (ret < 0) return ret;
    }
    switch(among_var) {
        case 0: return 0;
        case 1:
            {   int ret;
                ret = slice_from_s(z, 4, s_29); /* <-, line 118 */
                if (ret < 0) return ret;
            }
            break;
        case 2:
            {   int ret;
                ret = slice_from_s(z, 3, s_30); /* <-, line 119 */
                if (ret < 0) return ret;
            }
            break;
        case 3:
            {   int ret;
                ret = slice_from_s(z, 2, s_31); /* <-, line 120 */
                if (ret < 0) return ret;
            }
            break;
        case 4:
            {   int ret;
                ret = slice_from_s(z, 2, s_32); /* <-, line 122 */
                if (ret < 0) return ret;
            }
            break;
        case 5:
            {   int ret;
                ret = slice_del(z); /* delete, line 124 */
                if (ret < 0) return ret;
            }
            break;
        case 6:
            {   int ret = r_R2(z);
                if (ret == 0) return 0; /* call R2, line 126 */
                if (ret < 0) return ret;
            }
            {   int ret;
                ret = slice_del(z); /* delete, line 126 */
                if (ret < 0) return ret;
            }
            break;
    }
    return 1;
}

static int r_Step_4(struct SN_env * z) {
    int among_var;
    z->ket = z->c; /* [, line 131 */
    among_var = find_among_b(z, a_6, 18); /* substring, line 131 */
    if (!(among_var)) return 0;
    z->bra = z->c; /* ], line 131 */
    {   int ret = r_R2(z);
        if (ret == 0) return 0; /* call R2, line 131 */
        if (ret < 0) return ret;
    }
    switch(among_var) {
        case 0: return 0;
        case 1:
            {   int ret;
                ret = slice_del(z); /* delete, line 134 */
                if (ret < 0) return ret;
            }
            break;
        case 2:
            {   int m = z->l - z->c; (void) m; /* or, line 135 */
                if (!(eq_s_b(z, 1, s_33))) goto lab1;
                goto lab0;
            lab1:
                z->c = z->l - m;
                if (!(eq_s_b(z, 1, s_34))) return 0;
            }
        lab0:
            {   int ret;
                ret = slice_del(z); /* delete, line 135 */
                if (ret < 0) return ret;
            }
            break;
    }
    return 1;
}

static int r_Step_5(struct SN_env * z) {
    int among_var;
    z->ket = z->c; /* [, line 140 */
    among_var = find_among_b(z, a_7, 2); /* substring, line 140 */
    if (!(among_var)) return 0;
    z->bra = z->c; /* ], line 140 */
    switch(among_var) {
        case 0: return 0;
        case 1:
            {   int m = z->l - z->c; (void) m; /* or, line 141 */
                {   int ret = r_R2(z);
                    if (ret == 0) goto lab1; /* call R2, line 141 */
                    if (ret < 0) return ret;
                }
                goto lab0;
            lab1:
                z->c = z->l - m;
                {   int ret = r_R1(z);
                    if (ret == 0) return 0; /* call R1, line 141 */
                    if (ret < 0) return ret;
                }
                {   int m = z->l - z->c; (void) m; /* not, line 141 */
                    {   int ret = r_shortv(z);
                        if (ret == 0) goto lab2; /* call shortv, line 141 */
                        if (ret < 0) return ret;
                    }
                    return 0;
                lab2:
                    z->c = z->l - m;
                }
            }
        lab0:
            {   int ret;
                ret = slice_del(z); /* delete, line 141 */
                if (ret < 0) return ret;
            }
            break;
        case 2:
            {   int ret = r_R2(z);
                if (ret == 0) return 0; /* call R2, line 142 */
                if (ret < 0) return ret;
            }
            if (!(eq_s_b(z, 1, s_35))) return 0;
            {   int ret;
                ret = slice_del(z); /* delete, line 142 */
                if (ret < 0) return ret;
            }
            break;
    }
    return 1;
}

static int r_exception2(struct SN_env * z) {
    z->ket = z->c; /* [, line 148 */
    if (!(find_among_b(z, a_8, 8))) return 0; /* substring, line 148 */
    z->bra = z->c; /* ], line 148 */
    if (z->c > z->lb) return 0; /* atlimit, line 148 */
    return 1;
}

static int r_exception1(struct SN_env * z) {
    int among_var;
    z->bra = z->c; /* [, line 160 */
    among_var = find_among(z, a_9, 18); /* substring, line 160 */
    if (!(among_var)) return 0;
    z->ket = z->c; /* ], line 160 */
    if (z->c < z->l) return 0; /* atlimit, line 160 */
    switch(among_var) {
        case 0: return 0;
        case 1:
            {   int ret;
                ret = slice_from_s(z, 3, s_36); /* <-, line 164 */
                if (ret < 0) return ret;
            }
            break;
        case 2:
            {   int ret;
                ret = slice_from_s(z, 3, s_37); /* <-, line 165 */
                if (ret < 0) return ret;
            }
            break;
        case 3:
            {   int ret;
                ret = slice_from_s(z, 3, s_38); /* <-, line 166 */
                if (ret < 0) return ret;
            }
            break;
        case 4:
            {   int ret;
                ret = slice_from_s(z, 3, s_39); /* <-, line 167 */
                if (ret < 0) return ret;
            }
            break;
        case 5:
            {   int ret;
                ret = slice_from_s(z, 3, s_40); /* <-, line 168 */
                if (ret < 0) return ret;
            }
            break;
        case 6:
            {   int ret;
                ret = slice_from_s(z, 3, s_41); /* <-, line 172 */
                if (ret < 0) return ret;
            }
            break;
        case 7:
            {   int ret;
                ret = slice_from_s(z, 5, s_42); /* <-, line 173 */
                if (ret < 0) return ret;
            }
            break;
        case 8:
            {   int ret;
                ret = slice_from_s(z, 4, s_43); /* <-, line 174 */
                if (ret < 0) return ret;
            }
            break;
        case 9:
            {   int ret;
                ret = slice_from_s(z, 5, s_44); /* <-, line 175 */
                if (ret < 0) return ret;
            }
            break;
        case 10:
            {   int ret;
                ret = slice_from_s(z, 4, s_45); /* <-, line 176 */
                if (ret < 0) return ret;
            }
            break;
        case 11:
            {   int ret;
                ret = slice_from_s(z, 5, s_46); /* <-, line 177 */
                if (ret < 0) return ret;
            }
            break;
    }
    return 1;
}

static int r_postlude(struct SN_env * z) {
    if (!(z->B[0])) return 0; /* Boolean test Y_found, line 193 */
    while(1) { /* repeat, line 193 */
        int c = z->c;
        while(1) { /* goto, line 193 */
            int c = z->c;
            z->bra = z->c; /* [, line 193 */
            if (!(eq_s(z, 1, s_47))) goto lab1;
            z->ket = z->c; /* ], line 193 */
            z->c = c;
            break;
        lab1:
            z->c = c;
            if (z->c >= z->l) goto lab0;
            z->c++; /* goto, line 193 */
        }
        {   int ret;
            ret = slice_from_s(z, 1, s_48); /* <-, line 193 */
            if (ret < 0) return ret;
        }
        continue;
    lab0:
        z->c = c;
        break;
    }
    return 1;
}

extern int english_ISO_8859_1_stem(struct SN_env * z) {
    {   int c = z->c; /* or, line 197 */
        {   int ret = r_exception1(z);
            if (ret == 0) goto lab1; /* call exception1, line 197 */
            if (ret < 0) return ret;
        }
        goto lab0;
    lab1:
        z->c = c;
        {   int c_test = z->c; /* test, line 199 */
            {   int c = z->c + 3;
                if (0 > c || c > z->l) return 0;
                z->c = c; /* hop, line 199 */
            }
            z->c = c_test;
        }
        {   int c = z->c; /* do, line 200 */
            {   int ret = r_prelude(z);
                if (ret == 0) goto lab2; /* call prelude, line 200 */
                if (ret < 0) return ret;
            }
        lab2:
            z->c = c;
        }
        {   int c = z->c; /* do, line 201 */
            {   int ret = r_mark_regions(z);
                if (ret == 0) goto lab3; /* call mark_regions, line 201 */
                if (ret < 0) return ret;
            }
        lab3:
            z->c = c;
        }
        z->lb = z->c; z->c = z->l; /* backwards, line 202 */

        {   int m = z->l - z->c; (void) m; /* do, line 204 */
            {   int ret = r_Step_1a(z);
                if (ret == 0) goto lab4; /* call Step_1a, line 204 */
                if (ret < 0) return ret;
            }
        lab4:
            z->c = z->l - m;
        }
        {   int m = z->l - z->c; (void) m; /* or, line 206 */
            {   int ret = r_exception2(z);
                if (ret == 0) goto lab6; /* call exception2, line 206 */
                if (ret < 0) return ret;
            }
            goto lab5;
        lab6:
            z->c = z->l - m;
            {   int m = z->l - z->c; (void) m; /* do, line 208 */
                {   int ret = r_Step_1b(z);
                    if (ret == 0) goto lab7; /* call Step_1b, line 208 */
                    if (ret < 0) return ret;
                }
            lab7:
                z->c = z->l - m;
            }
            {   int m = z->l - z->c; (void) m; /* do, line 209 */
                {   int ret = r_Step_1c(z);
                    if (ret == 0) goto lab8; /* call Step_1c, line 209 */
                    if (ret < 0) return ret;
                }
            lab8:
                z->c = z->l - m;
            }
            {   int m = z->l - z->c; (void) m; /* do, line 211 */
                {   int ret = r_Step_2(z);
                    if (ret == 0) goto lab9; /* call Step_2, line 211 */
                    if (ret < 0) return ret;
                }
            lab9:
                z->c = z->l - m;
            }
            {   int m = z->l - z->c; (void) m; /* do, line 212 */
                {   int ret = r_Step_3(z);
                    if (ret == 0) goto lab10; /* call Step_3, line 212 */
                    if (ret < 0) return ret;
                }
            lab10:
                z->c = z->l - m;
            }
            {   int m = z->l - z->c; (void) m; /* do, line 213 */
                {   int ret = r_Step_4(z);
                    if (ret == 0) goto lab11; /* call Step_4, line 213 */
                    if (ret < 0) return ret;
                }
            lab11:
                z->c = z->l - m;
            }
            {   int m = z->l - z->c; (void) m; /* do, line 215 */
                {   int ret = r_Step_5(z);
                    if (ret == 0) goto lab12; /* call Step_5, line 215 */
                    if (ret < 0) return ret;
                }
            lab12:
                z->c = z->l - m;
            }
        }
    lab5:
        z->c = z->lb;
        {   int c = z->c; /* do, line 218 */
            {   int ret = r_postlude(z);
                if (ret == 0) goto lab13; /* call postlude, line 218 */
                if (ret < 0) return ret;
            }
        lab13:
            z->c = c;
        }
    }
lab0:
    return 1;
}

extern struct SN_env * english_ISO_8859_1_create_env(void) { return SN_create_env(0, 2, 1); }

extern void english_ISO_8859_1_close_env(struct SN_env * z) { SN_close_env(z); }

