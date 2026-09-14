/*
Makes an SQL table for silver, from a bronze table

Differs from the bronze table by:
- Removing all -Unit columns, as they contain only a single non-null value.
- Removing storeName, as all values are null.
- Removing rows where -Amount is null, as they can't be ranked.
- All numerical values are cast to double.
*/

CREATE OR REPLACE TABLE product_nutritiens_silver AS
SELECT
  chain,
  title,
  brand,
  slugifiedUrl AS website_url,
  imagePath AS image_path,

  CAST(pricePerUnit AS DOUBLE) AS price_per_unit,
  CAST(comparePricePerUnit AS DOUBLE) AS compare_price_per_unit,
  compareUnit AS compare_unit,

  subtitle,
  description,
  ean,

  CAST(energyAmount AS DOUBLE) AS energy_amount,
  CAST(caloriesAmount AS DOUBLE) AS calories_amount,
  CAST(fatAmount AS DOUBLE) AS fat_amount,
  CAST(saturatedFatAmount AS DOUBLE) AS saturated_fat_amount,
  CAST(carbohydratesAmount AS DOUBLE) AS carbohydrates_amount,
  CAST(sugarsAmount AS DOUBLE) AS sugars_amount,
  CAST(proteinAmount AS DOUBLE) AS protein_amount,
  CAST(saltAmount AS DOUBLE) AS salt_amount

FROM hybrid_test.default.product_nutritiens_bronze
WHERE energyAmount IS NOT NULL
  AND caloriesAmount IS NOT NULL
  AND fatAmount IS NOT NULL
  AND saturatedFatAmount IS NOT NULL
  AND carbohydratesAmount IS NOT NULL
  AND sugarsAmount IS NOT NULL
  AND proteinAmount IS NOT NULL
  AND saltAmount IS NOT NULL;