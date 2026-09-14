/*
Makes an SQL table for bronze, from a products table. The products table is made directly from a json file in the blob
*/

CREATE OR REPLACE TABLE product_nutritiens_bronze AS
SELECT
  chain,

  get_json_object(product_json, '$.title') AS title,
  get_json_object(product_json, '$.brand') AS brand,
  get_json_object(product_json, '$.slugifiedUrl') AS slugifiedUrl,
  get_json_object(product_json, '$.imagePath') AS imagePath,

  CAST(get_json_object(product_json, '$.pricePerUnit') AS STRING) AS pricePerUnit,
  CAST(get_json_object(product_json, '$.comparePricePerUnit') AS STRING) AS comparePricePerUnit,
  get_json_object(product_json, '$.compareUnit') AS compareUnit,

  get_json_object(product_json, '$.subtitle') AS subtitle,
  get_json_object(product_json, '$.description') AS description,
  get_json_object(product_json, '$.store.name') AS storeName,
  get_json_object(product_json, '$.ean') AS ean,

  CAST(get_json_object(product_json, '$.nutritionalContent[0].amount') AS STRING) AS energyAmount,
  get_json_object(product_json, '$.nutritionalContent[0].unit') AS energyUnit,

  CAST(get_json_object(product_json, '$.nutritionalContent[1].amount') AS STRING) AS caloriesAmount,
  get_json_object(product_json, '$.nutritionalContent[1].unit') AS caloriesUnit,

  CAST(get_json_object(product_json, '$.nutritionalContent[2].amount') AS STRING) AS fatAmount,
  get_json_object(product_json, '$.nutritionalContent[2].unit') AS fatUnit,

  CAST(get_json_object(product_json, '$.nutritionalContent[3].amount') AS STRING) AS saturatedFatAmount,
  get_json_object(product_json, '$.nutritionalContent[3].unit') AS saturatedFatUnit,

  CAST(get_json_object(product_json, '$.nutritionalContent[4].amount') AS STRING) AS carbohydratesAmount,
  get_json_object(product_json, '$.nutritionalContent[4].unit') AS carbohydratesUnit,

  CAST(get_json_object(product_json, '$.nutritionalContent[5].amount') AS STRING) AS sugarsAmount,
  get_json_object(product_json, '$.nutritionalContent[5].unit') AS sugarsUnit,

  CAST(get_json_object(product_json, '$.nutritionalContent[6].amount') AS STRING) AS proteinAmount,
  get_json_object(product_json, '$.nutritionalContent[6].unit') AS proteinUnit,

  CAST(get_json_object(product_json, '$.nutritionalContent[7].amount') AS STRING) AS saltAmount,
  get_json_object(product_json, '$.nutritionalContent[7].unit') AS saltUnit

FROM products
WHERE CAST(get_json_object(product_json, '$.comparePricePerUnit') AS STRING) > '0'
  AND get_json_object(product_json, '$.compareUnit') IN ('kg', 'l');