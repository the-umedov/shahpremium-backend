"""Advocates moduli.

MUHIM: asl loyihada `advocates.module.js` boʻsh stub (controller/service/provider
yoʻq — faqat `@Module({ imports: [], controllers: [], providers: [], exports: [] })`).
Shu sababli bu yerda ham hech qanday endpoint yaratilmagan — faqat boʻsh router.
`Advocate` jadvali (app.models.models.Advocate) mavjud, lekin uni ochib beruvchi
CRUD original kodda hech qachon yozilmagan.
"""

from fastapi import APIRouter

router = APIRouter(tags=["advocates"])
