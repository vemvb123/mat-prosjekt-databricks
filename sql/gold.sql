/*
Makes an SQL table for silver, from a bronze table

Differs from the bronze table by:
- Adding the first part of the link, for website/image links
- Changing brand values to 'Ikke spesifisert' hvis verdien er null
- Changing description values to 'Ingen beskrivelse' hvis verdien er null
- Multiplying unit values with 10
*/

CREATE OR REPLACE TABLE product_nutritiens_gold AS
SELECT
  chain,
  title,

  CASE
    WHEN brand IS NULL THEN 'Ikke spesifisert'
    ELSE brand
  END AS brand,

  CASE
    WHEN description IS NULL THEN 'Ingen beskrivelse'
    ELSE description
  END AS description,

  CASE
    WHEN LOWER(chain) = 'spar' THEN concat('https://spar.no', website_url)
    ELSE concat('https://meny.no', website_url)
  END AS website_url,

  concat(
    'https://bilder.ngdata.no/',
    regexp_replace(image_path, '^/+', ''),
    '/large.jpg'
  ) AS image_url,

  price_per_unit,
  compare_price_per_unit,
  compare_unit,

  subtitle,
  ean,

  energy_amount,
  calories_amount,
  fat_amount,
  saturated_fat_amount,
  carbohydrates_amount,
  sugars_amount,
  protein_amount,
  salt_amount,

  energy_amount * 10 AS energy_per_package,
  calories_amount * 10 AS calories_per_package,
  fat_amount * 10 AS fat_per_package,
  saturated_fat_amount * 10 AS saturated_fat_per_package,
  carbohydrates_amount * 10 AS carbohydrates_per_package,
  sugars_amount * 10 AS sugars_per_package,
  protein_amount * 10 AS protein_per_package,
  salt_amount * 10 AS salt_per_package,

  ROUND((energy_amount * 10) / compare_price_per_unit, 2) AS energy_per_nok,
  ROUND((calories_amount * 10) / compare_price_per_unit, 2) AS calories_per_nok,
  ROUND((fat_amount * 10) / compare_price_per_unit, 2) AS fat_per_nok,
  ROUND((saturated_fat_amount * 10) / compare_price_per_unit, 2) AS saturated_fat_per_nok,
  ROUND((carbohydrates_amount * 10) / compare_price_per_unit, 2) AS carbohydrates_per_nok,
  ROUND((sugars_amount * 10) / compare_price_per_unit, 2) AS sugars_per_nok,
  ROUND((protein_amount * 10) / compare_price_per_unit, 2) AS protein_per_nok,
  ROUND((salt_amount * 10) / compare_price_per_unit, 2) AS salt_per_nok

FROM hybrid_test.default.product_nutritiens_silver;