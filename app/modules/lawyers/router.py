"""Lawyers moduli.

MUHIM: asl loyihada `lawyers.module.js` boʻsh stub (controller/service/provider
yoʻq — faqat `@Module({ imports: [], controllers: [], providers: [], exports: [] })`).
Shu sababli bu yerda ham hech qanday endpoint yaratilmagan — faqat boʻsh router.
`Lawyer` jadvali (app.models.models.Lawyer) mavjud, lekin uni ochib beruvchi
CRUD original kodda hech qachon yozilmagan.
"""

from fastapi import APIRouter

router = APIRouter(tags=["lawyers"])
