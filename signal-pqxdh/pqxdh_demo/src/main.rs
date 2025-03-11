use rand::rngs::OsRng;
use libsignal_protocol::kem::{KeyPair, KeyType, PublicKey, SecretKey};
use libsignal_protocol::state::{PreKeyId, SignedPreKeyId, KyberPreKeyId};
use libsignal_protocol::ciphertext_message::{PreKeySignalMessage, SignalMessage};
use libsignal_protocol::curve25519::{PrivateKey, PublicKey as CurvePublicKey};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut csprng = OsRng;

    // Alice and Bob generate their long-term identity key pairs
    let alice_identity_key_pair = KeyPair::generate(KeyType::Kyber1024);
    let bob_identity_key_pair = KeyPair::generate(KeyType::Kyber1024);

    // Bob generates a signed pre-key and a one-time pre-key
    let bob_signed_pre_key_pair = KeyPair::generate(KeyType::Kyber1024);
    let bob_one_time_pre_key_pair = KeyPair::generate(KeyType::Kyber1024);

    // Alice initiates the key exchange by generating an ephemeral key pair
    let alice_ephemeral_key_pair = KeyPair::generate(KeyType::Kyber1024);

    // Alice creates a PreKeySignalMessage to send to Bob
    let pre_key_message = PreKeySignalMessage::new(
        4, // Message version
        123, // Registration ID
        Some(PreKeyId::from(1)), // PreKey ID
        SignedPreKeyId::from(1), // Signed PreKey ID
        Some(KyberPreKeyId::from(1)), // Kyber PreKey ID
        alice_ephemeral_key_pair.public_key.clone(), // Base key
        alice_identity_key_pair.public_key.clone(), // Identity key
        SignalMessage::new( // Signal message (dummy for demo)
            4,
            &[0u8; 32], // MAC key
            alice_ephemeral_key_pair.public_key.clone(),
            1, // Counter
            0, // Previous counter
            &[0u8; 32], // Ciphertext
            &alice_identity_key_pair.public_key.clone().into(),
            &bob_identity_key_pair.public_key.clone().into(),
        )?,
    )?;

    // Bob receives the PreKeySignalMessage and processes it
    let received_pre_key_message = PreKeySignalMessage::try_from(pre_key_message.serialized().as_ref())?;

    // Bob derives the shared secret using his private keys and the received message
    let shared_secret = bob_identity_key_pair.secret_key.decapsulate(
        &received_pre_key_message.kyber_ciphertext().unwrap()
    )?;

    println!("Shared secret derived by Bob: {:?}", shared_secret);

    // Bob sends a response back to Alice (not shown in this demo)

    Ok(())
}