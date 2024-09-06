# Аутентификация в FastAPI | Basic Auth, Cookie Auth, Token Auth

### Аутентификация

Определение: Аутентификация — это процесс проверки, кто вы есть. Он включает в себя подтверждение личности пользователя 
на основе предоставленных им учетных данных, таких как логин и пароль, биометрические данные или токены. 

Цель: Цель аутентификации — подтвердить, что пользователь является тем, за кого он себя выдает.

Примеры:
- Ввод логина и пароля на сайте.
- Использование биоматрикс, например, отпечатка пальца или распознавания лица.
- Применение двухфакторной аутентификации (2FA), когда пользователю необходимо ввести дополнительный код, отправленный 
на его мобильный телефон.

### Авторизация

Определение: Авторизация — это процесс определения прав доступа пользователя после его аутентификации. Он определяет, 
на что пользователь имеет права, основываясь на его роли, учетной записи или других атрибутах.

Цель: Цель авторизации — управлять доступом к ресурсам и действиям для различных пользователей.

Примеры:
- Пользователь с ролью «администратор» имеет доступ ко всем функциям системы, тогда как пользователь с ролью «гость» 
может просматривать только определенные страницы.
- Веб-приложение, которое позволяет пользователю редактировать свои данные, но не позволяет ему редактировать данные 
других пользователей.
- Уровни доступа к библиотекам или документам в зависимости от роли (например, читатель, редактор, администратор).


# JWT Auth в FastAPI

JWT - json web token. Состоит из 3 элементов разделенных между собой точкой. Посмотреть что это такое вы можете на 
сайте - jwt.io.
1. HEADER - содержит в себе служебную информацию для того чтобы приложению которое расшифровывает токен, было понятно
что с этим делать
   ```
   {
     "alg": "RS256",
     "typ": "JWT"
   }
   ```
2. PAYLOAD (Полезная нагрузка) - данные которые мы получаем от пользователя или наоборот пользователь от нас
   ```
   {
      "type": "access",
      "sub": 4,
      "username": "admin",
      "email": "user@example.com",
      "exp": 1725429100,
      "iat": 1725428200
   }
   ```

3. VERIFY SIGNATURE (Подпись) - состоит из сложенных данных HEADER и PAYLOAD + secret(секретный токен который лежит на сервере).
Токен также может быть зашифрован при помощи secret key, а расшифрован при помощи public key. Пользователь на свою 
сторону получает только public key и при помощи него проверяет зашифрованные с помощью secret key данные, валидны ли они
и от кого пришли.

Для выпуска JWT мы будем использовать библиотеку **pyJWT** c шифрованием "RS256"

## Строим нашу JWT auth

1. Установить библиотеку можно с помощью команды:
   - poetry add "pyjwt[crypto]"
2. Сгенерируем public и secret key
   - скопируйте команды для создания ключей из *src/auth/README.md*
   - создайте папку certs и выполните команды
   - не забудьте добавить /certs в .gitignore
3. Укажем в нашем core/config пути к нашим ключам
   ```
   src/core/config
   
   class AuthJWT(BaseModel):
     private_key_path: Path = BASE_DIR / "src" / "certs" / "jwt-private.pem"
     public_key_path: Path = BASE_DIR / "src" / "certs" / "jwt-public.pem"
     algorithm: str = "RS256"
     access_token_expire_minutes: int = 15
   ```
4. Напишем функции которые помогут создавать токены и парсить их.
   ```
   src/auth/utils.py
   
   def encode_jwt():
       """Функция для кодирования данных в JWT"""
       pass
       
   def decode_jwt():
      """Функция для расшифровки JWT"""
      pass
   ```
5. Прежде чем выдавать пользователю токен, нужно его аутонтефицировать, для этого напишем эндпоинт с аутентификацией
   - добавим schemas для валидации пользователя
   ```
   src/api_v1/schemas/user_schemas.py
      
   class UserSchema(BaseModel):
      pass
   
   class UserOut(UserSchema):
      pass
   ```
   - добавим функции для шифровки и проверки пароля с помощью библиотеки bcrypt
   ```
   src/auth/utils
   
   poetry add bcrypt
   
   def hash_password(password: str) -> bytes:
       """Функция для шифрования пароля"""
       pass
   
   def validate_password(
       password: str,
       hashed_password: bytes,
   ) -> bool:
       """Функция для проверки соответствия пароля"""
       pass   
   ```
6. Создаем роутер для создания юзера
   ```
   src/api_v1/routers/user_router.py
   
   @router.post(
       "/register",
       response_model=UserOut,
       status_code=status.HTTP_201_CREATED,
   )
   async def register_user(
       user_in: UserSchema,
       session: AsyncSession = Depends(db_helper.get_db),
   ):
       return await create_user(session=session, user_in=user_in)
   ```
7. Создаем роутер для аутентификации по логину и паролю, который после проверки пользователя сгенерирует JWT токен
   - для начала создадим валидатор для возвращаемого токена
   ```
   src/api_v1/schemas/token_schemas.py
   
   class TokenInfo(BaseModel):
       access_token: str
       token_type: str
   ```
   - создаем роутер для аутентификации
   ```
   src/api_v1/routers/demo_jwt_auth.py
   
   @router.post("/login", response_model=TokenInfo)
   async def login(
       user: UserSchema = Depends(validate_auth_user),
   ) -> TokenInfo:
      pass
   ```
   - создаем функцию которая будет валидировать логин и пароль введеные юзером
   ```
   src/api_v1/dependencies/security_dependencies.py
   
   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")
   
   async def validate_auth_user(
       # form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
       username: str = Form(...),
       password: str = Form(...),
       session: AsyncSession = Depends(db_helper.get_db),
   ) -> UserOut:
      pass
   ```
8. Напишем эндпоинт для получения информации о себе
   ```
   src/api_v1/routers/user_router.py
   
   @router.get("/users/me/", response_model=UserOut)
   async def read_users_me(
       payload: dict = Depends(get_current_token_payload),
       user: UserSchema = Depends(get_current_active_auth_user),
   ):
       return user
   ```
   - напишем зависимость для получения активного юзера
   ```
   src/api_v1/dependencies/security_dependencies.py
   
   def get_current_active_auth_user(
       user: UserSchema = Depends(get_current_auth_user),
   ):
       """Функция для проверки активен ли юзер"""
       pass
   ```
   - напишем зависимость для получения аутентифицированного пользователя
   ```
   src/api_v1/dependencies/security_dependencies.py
   
   async def get_current_auth_user(
       payload: dict = Depends(get_current_token_payload),
       session: AsyncSession = Depends(db_helper.get_db),
   ):
       """Из полезной нагрузки получаем юзера из БД"""
       pass
   ```
   - напишем зависимость для получения полезной нагрузки из заголовка Authorization
   ```
   src/api_v1/dependencies/security_dependencies.py
   
   def get_current_token_payload(
       credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
   ):
       """Берем из заголовка Authorization JWT, декодируем и возвращаем полезную нагрузку"""
       pass
   ```

