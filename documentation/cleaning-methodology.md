# Data Cleaning and Preparation Methodology

## 1. Overview

As part of the FAIRification of the library catalogue dataset, data preparation and cleaning were performed using OpenRefine. The purpose of this process was to inspect the original dataset, identify data-quality issues, improve consistency where appropriate, and prepare the data for subsequent semantic modelling and RDF generation.

The cleaning process aimed to preserve the original meaning of the data while making the resulting dataset more consistent, understandable, and suitable for reuse.

## 2. Source Dataset

- **Dataset name:** Library Catalogue
- **Source:** Kaggle — [Library Catalogue](https://www.kaggle.com/datasets/neramarkovi/library-catalog)
- **Original file format:** CSV
- **Original number of records:** 2,104
- **Original number of columns:** 18
- **Tool used:** OpenRefine 3.10.0
- **Final number of records:** 2077
- **Final number of columns:** 13

The original dataset was retained separately from the cleaned version to preserve the source data and enable comparison between the original and modified datasets.

## 3. Data Inspection

The dataset was imported into OpenRefine and inspected to understand its structure, identify relevant fields, and detect potential data inconsistencies.

The inspection focused on:

- Missing values in the `catalogue_position` field.
- Missing values in other important fields such as `title`.
- Inconsistent representations of categories and types, in attributes such as `genre` and `section`.
- Duplicate record entries.
- Potential formatting inconsistencies, including unnecessary whitespace.
- Data types and values in numerical fields such as `year_published` and `ratings`.
- Attributes that were not required for the project's intended reuse scenarios.
- Appropriate naming of the chosen attributes.

OpenRefine facets and other inspection features were used where appropriate to examine distinct values, identify blank cells, and investigate possible inconsistencies.

## 4. Data Cleaning Operations

### 4.1 Handling Missing Catalogue Identifiers

The `catalogue_position` field was treated as the primary unique identifier for records in the source dataset. Rows in which this field was blank were removed during cleaning, because they did not contain the identifier required for record-identification. The absence of a catalogue position does not necessarily mean that the other information in a row is invalid or unusable. 

The assignment of new `catalogue_position` values to these records was not possible as the pattern behind the assignment of these positions was not identifiable.

Therefore, this can be considered an assumption and a limitation of the cleaning process. The number of rows removed and the number of records remaining should be reported below.

- Rows removed because `catalogue_position` was blank: 7

### 4.2 Text Cleaning and Standardization

- The `catalogue_position` field had many duplicate values that contained identical information to other rows, therefore 10 of those duplicate records were deleted after comparing the data in the respective duplicate records.
  
- The rows with empty `title` values were removed from the dataset, as its difficult to identify the book with other available details (10 records removed).
  
- Renamed all columns using lowercase text and underscores to follow a standardized naming system in the dataset.
  
- Text Facets were applied to columns with categories, to identify category naming inconsistencies. The categories with similar contexts and meaning were merged to remove discrepancies.
    - Transform the `language` codes to lowercase.
      
      <img width="569" height="234" alt="image" src="https://github.com/user-attachments/assets/57034e28-f7a7-409b-a790-11e763113f3f" />

    - In column `language`, the `en` and `eng` were merged to `en`, as both language codes stand for the English language.
      
      <img width="290" height="282" alt="image" src="https://github.com/user-attachments/assets/67712bad-8a45-449f-912f-7d6fa881a4ff" />

    - In column `genre`, the genre categories merged are:
        - `Classic` and `Classic Literature` merged to `Classic Literature`.
          
          <img width="268" height="131" alt="image" src="https://github.com/user-attachments/assets/2ccce383-7f37-46bc-a7e4-521fb6bb9fe6" />

        - `Religion & Spirituality`, `Religion, Spirituality`, `Spirituality` and `Religion` merged to `Religion & Spirituality`.
          
          <img width="267" height="229" alt="image" src="https://github.com/user-attachments/assets/0f7b81b7-b48e-4848-bf21-5787ed57a044" />
      
          <img width="274" height="154" alt="image" src="https://github.com/user-attachments/assets/d8c57c0a-20ac-4848-9a38-436a1a1c97f8" />
          
          <img width="275" height="263" alt="image" src="https://github.com/user-attachments/assets/1f382893-f5ec-41ef-ad62-8961278c30f8" />

        - `Music` and `Music/Songbooks` merged to `Music`.
          
           <img width="256" height="41" alt="image" src="https://github.com/user-attachments/assets/86bc7ab0-a0ad-493b-b5bc-d54a8dbf996a" />

        - `Epic Poetry` and `Poetry` merged to `Poetry`.
          
        - `Children's Stories`, `Children's Literature` and `Children's Fiction` merged to `Children's Fiction`.
          
          <img width="243" height="19" alt="image" src="https://github.com/user-attachments/assets/bf698cfa-ab7a-48bb-8d99-38d5aacb84fc" />
          
          <img width="263" height="43" alt="image" src="https://github.com/user-attachments/assets/642cc594-2fd8-4523-8713-a957e689b182" />

        - `Historical` and `Historical Fiction` merged to `Historical Fiction`.
          
          <img width="267" height="39" alt="image" src="https://github.com/user-attachments/assets/f9730415-1155-4211-8ba6-c4dae39f2d22" />

    - In column `section`, the categories merged are:
        - `Children`, `Children's` and `Children's Fiction` merged to `Children`.
        - `Young Adult` and `Young Adult (YA)` merged to `Young Adult`.
          
          <img width="275" height="349" alt="image" src="https://github.com/user-attachments/assets/69d75c68-2024-478d-b3f6-bc821819efd4" />

          <img width="270" height="283" alt="image" src="https://github.com/user-attachments/assets/8c88e05a-2e7c-414d-a496-6baad127d432" />


### 4.3 Numerical Data

Numerical values were converted to suitable data types. Values that could not be interpreted reliably were investigated and replaced with blank when necessary.

The columns `year_published`, `times_borrowed`, `price`, `rating` and `ratings_count` had numerical data, and were inspected for data type and values inconsistencies. The above mentioned columns had their values input as text values, therefore the values were converted to the respective numeric formats.

- The values in column `year` were converted to integer values.
    - Values that had non-numeric characters, such as'16th century', were converted to a blank value.
    - Inaccurate year values, such as '2119', were converted to blank.
      
      <img width="259" height="126" alt="image" src="https://github.com/user-attachments/assets/b3fdc8b4-4ff5-47dc-b9d5-63fedc1cb5be" />

      <img width="270" height="38" alt="image" src="https://github.com/user-attachments/assets/6e088173-c11f-48b2-8820-c34dd76df967" />

- The values in column `times_borrowed` were converted to integer values.

  <img width="273" height="353" alt="image" src="https://github.com/user-attachments/assets/9caec70f-f74d-4370-80a0-9cb9122de4f7" />

- The values in column `rating` were converted to decimal values, by removing the text suffix 'out of 5 stars' from the values.
  
  <img width="207" height="469" alt="image" src="https://github.com/user-attachments/assets/75737919-09d5-4d33-95f6-9f6bf3a5aaeb" />

- The values in column `ratings_count` were converted to integer values.
  
  <img width="243" height="488" alt="image" src="https://github.com/user-attachments/assets/f117205b-769e-43c7-9415-d37af4a8e4ad" />

- The values in column `price` were converted to numeric values, by removing the text prefix '$' from the values.

  <img width="147" height="492" alt="image" src="https://github.com/user-attachments/assets/cf832300-b224-4064-833a-dc64d28eba54" />


### 4.4 Missing Values

[Describe how missing values were handled in the retained columns.]

Missing values were distinguished from numerical zero and other legitimate values. No value was inferred or imputed unless the decision could be justified by the source data or a documented rule.

### 4.5 Removal of Unnecessary Columns

Columns considered unnecessary for the selected reuse scenarios were removed from the cleaned dataset.

The removed columns included:

- `last_borrowed_date`
- `total_copies`
- `page_count`
- `dimensions`
- `thumbnails`
  
The reasons for removal were:
- Columns such as `dimensions`, `thumbnails` and `page_count` signify the physical attributes of the book, which seem irrelevant to the intended use of the library dataset. Such physical attributes don't influence the demand, price or category of the book, thereby not helping in performing sales/demand analysis on the books.

- This dataset is intended to replicate/assist a library catalogue. The `total_copies` attribute would be more useful in a book inventory setting, where the number of copies produced or in stock can be useful information.

- `last_borrowed_date` attribute doesn't convey any information on the genre, section or popularity of the book. Knowing that information doesn't help us in the intended use of this data. 

The original dataset was retained separately so that the removed information remained distinguishable from information that was never present in the source.

## 5. Validation

After cleaning, the dataset was checked to assess whether the intended changes had been applied correctly.

The following checks were performed or should be completed before publication:

- Confirming the final record count.
- Confirming the final number and names of columns.
- Checking that the retained `catalogue_position` values were populated.
- Checking for duplicate catalogue positions.
- Reviewing transformed fields for unexpected or invalid values.
- Confirming that the cleaned file could be exported and reopened successfully.

Validation results:

- Original records: 2,104
- Final records: 2077
- Original columns: 18
- Final columns: 13
- Duplicate catalogue positions identified: 547, 870, 1346, 1347, 1378, 1550, 1659, 1698, ,1928, 1991.
- Blank catalogue positions identified: 76, 114, 153, 213, 699, 927, 1395.
- Blank title positions: 255, 376, 587, 654, 658, 1224, 1579, 1969, 2047, 2064.
- Unresolved data-quality issues: [describe, or state none only if verified]

## 6. Output and Reproducibility

The outputs of the data-preparation stage are stored in the project repository.

- **Original dataset:** `data/library_catalogue_original.csv`
- **Cleaned dataset:** `data/library_catalogue_clean.csv`
- **Cleaning methodology:** `documentation/cleaning-methodology.md`
- **OpenRefine operation history:** `documentatn/openrefine-operations.json`

The cleaning methodology and OpenRefine operation history provide additional evidence of the transformations performed. Screenshots may also be included to illustrate representative operations.

## 7. Assumptions and Limitations

- The cleaning process involved decisions about which records and fields to retain. In particular, the removal of rows with blank `catalogue_position` values assumed that the source identifier was necessary for retaining a record in the cleaned dataset.

- This assumption may exclude records that contain useful bibliographic information but lack the expected catalogue identifier. The effect of this decision should be considered when interpreting the final dataset.

- The removal of columns also limits the types of questions that can be answered using the cleaned dataset. The original dataset is therefore preserved separately.

