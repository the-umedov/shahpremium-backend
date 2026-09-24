-- CLIENT roli bor, lekin `clients` jadvalida profili yo'q foydalanuvchilarga profil yaratadi.
-- Profilsiz mijoz uchun backend "Mijoz profili topilmadi" (403) qaytaradi — ro'yxatdan
-- o'tish avval profil yaratmagani uchun shunday foydalanuvchilar paydo bo'lgan.
-- Idempotent: profili bor foydalanuvchiga tegmaydi.
INSERT INTO public.clients (id, "userId", code, "fullName", "clientType", email, phone, "createdAt", "updatedAt")
SELECT
    gen_random_uuid()::text,
    u.id,
    'CL-' || upper(substr(md5(u.id), 1, 10)),
    COALESCE(NULLIF(trim(concat_ws(' ', p."firstName", p."lastName")), ''), u.email),
    'INDIVIDUAL',
    u.email,
    u.phone,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM public.users u
JOIN public.user_roles ur ON ur."userId" = u.id
JOIN public.roles r ON r.id = ur."roleId" AND r.key = 'CLIENT'
LEFT JOIN public.profiles p ON p."userId" = u.id
WHERE u."deletedAt" IS NULL
  AND NOT EXISTS (SELECT 1 FROM public.clients c WHERE c."userId" = u.id);
