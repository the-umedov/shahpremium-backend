-- Viloyatlar ichidagi tumanlar. Idempotent: har deploy'da qayta ishga tushsa ham xavfsiz.
CREATE TABLE IF NOT EXISTS public.districts (
    id text NOT NULL,
    name text NOT NULL,
    "regionId" text NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    CONSTRAINT districts_pkey PRIMARY KEY (id),
    CONSTRAINT "districts_regionId_fkey" FOREIGN KEY ("regionId")
        REFERENCES public.regions(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS "districts_regionId_name_key" ON public.districts USING btree ("regionId", name);
