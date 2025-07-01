from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Bloque principal para pruebas desde consola
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Password hasher utility")
    parser.add_argument("password", help="Contraseña en texto plano")
    parser.add_argument("--verify", help="Hash para verificar la contraseña (opcional)", default=None)

    args = parser.parse_args()

    if args.verify:
        success = verify_password(args.password, args.verify)
        if success:
            print("✅ Contraseña válida.")
        else:
            print("❌ Contraseña incorrecta.")
    else:
        hashed = hash_password(args.password)
        print(f"🔐 Hash generado:\n{hashed}")