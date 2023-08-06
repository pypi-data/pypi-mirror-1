#ifndef _SEAL2_INCLUDED_
#define _SEAL2_INCLUDED_

#ifdef __cplusplus
extern "C" {
#endif

#define WORDS_PER_SEAL2_CALL 1024

typedef struct _seal_ctx {
    unsigned long t[520]; /* 512 rounded up to a multiple of 5 + 5 */
    unsigned long s[265]; /* 256 rounded up to a multiple of 5 + 5 */
    unsigned long r[20]; /* 16 rounded up to multiple of 5 */
    unsigned long counter; /* 32-bit synch value. */
    unsigned long ks_buf[WORDS_PER_SEAL2_CALL];
    int ks_pos;
} seal_ctx;

/*** Initialize the SEAL2 context with a specific key.
 */
void seal_key(seal_ctx *c, unsigned char *key);

/*** Encrypt a plaintext.
 *
 * The ciphertext will always have the same size as the plaintext.
 *
 * \param[in] c  The SEAL2 context
 * \param[in] plaintext  The plaintext to be encrypted
 * \param[in] size  The size of the plaintext buffer
 * \param[out] ciphertext  The output buffer
 */
void seal_encrypt(seal_ctx *c, const unsigned char *plaintext, int size,
    unsigned char *ciphertext);

/** Decrypt a ciphertext
 *
 * The ciphertext will always have the same size as the plaintext.
 *
 * \param[in] c  The SEAL2 context
 * \param[in] ciphertext  The plaintext to be encrypted
 * \param[in] size  The size of the ciphertext buffer
 * \param[out] plaintext  The output buffer
 */
void seal_decrypt(seal_ctx *c, const unsigned char *ciphertext, int size,
    unsigned char *plaintext);

#ifdef __cplusplus
}
#endif

#endif

