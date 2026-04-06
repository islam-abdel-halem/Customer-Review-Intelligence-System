# Customer Review Intelligence System - Strategy Report

## 1. Project Overview

This project uses raw customer reviews for the Redmi 6 product to design a review intelligence solution that helps a business convert unstructured feedback into product and customer-experience decisions. The dataset contains **280 reviews** across **7 raw fields**:

- Review Title
- Customer name
- Rating
- Date
- Category
- Comments
- Useful

The reviews cover a short period from **15 September 2018** to **2 October 2018** and appear to represent customer feedback collected from an e-commerce product page.

## 2. Proposed Business Problem

### Business Problem Statement

**Identify the product categories and review themes that drive low customer satisfaction for Redmi 6, so the business can prioritize product fixes and support interventions.**

### Why this problem fits the data

The dataset is best suited for issue detection and prioritization rather than long-term forecasting because it focuses on one product and only spans 17 review dates. Even with that limitation, it already contains strong signals:

- Overall average extracted rating is **3.92 / 5**
- **52 reviews (18.6%)** are rated **1 or 2 stars**
- The **Camera** category has the weakest average rating at **2.86 / 5**
- The **Camera** category also has the highest share of low ratings at **42.9%**

These patterns suggest a practical, measurable business goal: detect the areas causing dissatisfaction and use them to guide product improvement, listing optimization, and customer support messaging.

### Measurable Objective

Create a review intelligence workflow that can:

1. Classify reviews into structured issue categories and sentiment levels.
2. Rank categories by dissatisfaction severity using rating and text signals.
3. Surface the top complaint themes behind 1-star and 2-star reviews.

### Example KPIs

- Percentage of low-rated reviews by category
- Average rating by category
- Volume of negative comments for each theme
- Percentage of reviews successfully assigned to a clean category and sentiment label

## 3. Raw Data Profiling

Initial profiling of the raw CSV shows that the dataset is usable, but several quality issues must be resolved before modeling.

### Structure and content observations

- Total rows: **280**
- Total columns: **7**
- All columns are currently stored as **text/object** data types
- Rating values are embedded in strings such as `"4.0 out of 5 stars"`
- Date values are embedded in strings such as `"on 1 October 2018"`
- The `Useful` field mixes blanks with text such as `"7 people found this helpful"`

### Distribution highlights

- Rating distribution:
  - 1-star: **43**
  - 2-star: **9**
  - 3-star: **27**
  - 4-star: **50**
  - 5-star: **151**
- Category distribution:
  - Others: **180**
  - Display: **36**
  - Battery: **29**
  - Camera: **28**
  - Delivery: **7**

### Potential data quality issues

1. **Incorrect data types**
   - `Rating`, `Date`, and `Useful` are text fields but should be converted into structured numeric/date fields.

2. **Missing or sparse values**
   - `Useful` has **170 null values** and **209 blank-like values**, making it highly incomplete.

3. **Inconsistent formatting**
   - Ratings include descriptive text instead of numeric values.
   - Dates include the prefix `"on "` and need normalization.
   - `Useful` stores counts as sentences rather than integers.

4. **Encoding problems**
   - The file is not UTF-8 and required **CP1252** decoding.
   - Visible replacement characters (`�`) appear in titles and comments, indicating character corruption or export issues.

5. **Duplicate or repeated content**
   - There are **21 exact duplicate rows**.
   - There are **36 duplicate reviews** when comparing title, customer, date, and comment together.
   - Review titles are repeated often, with **82 duplicated titles**.

6. **Class imbalance**
   - The `Category` field is dominated by `Others` (**180 / 280** reviews), which may weaken category-level modeling.

7. **Uneven text quality**
   - Comment length ranges from **2** to **4,577** characters.
   - **108 comments** are shorter than 20 characters, which may limit the value of NLP-based theme extraction for some records.

## 4. Data Science Life Cycle Plan

## 4.1 Collection

Goal: confirm the source, scope, and meaning of the raw review data.

Planned actions:

- Validate the origin of the dataset and document its source system.
- Confirm the business meaning of each field, especially `Category` and `Useful`.
- Capture metadata such as extraction date, file encoding, and row count.
- If possible in later phases, collect additional review snapshots for more reliable trend analysis over time.

Output of this stage:

- Raw data inventory
- Data dictionary
- Versioned source file archive

## 4.2 Cleaning

Goal: transform the raw CSV into an analysis-ready dataset.

Planned actions:

- Convert `Rating` into a numeric score from 1 to 5.
- Parse `Date` into a standard date type.
- Extract integer values from `Useful` and treat blanks as missing.
- Standardize text encoding and repair or flag corrupted characters.
- Trim whitespace and normalize inconsistent casing where needed.
- Detect and remove exact duplicates and define rules for handling near-duplicate reviews.
- Create quality flags for short comments, missing usefulness counts, and suspect records.

Output of this stage:

- Cleaned review table
- Data quality report
- Reproducible cleaning script

## 4.3 Exploration

Goal: understand the patterns, pain points, and opportunities in customer feedback.

Planned actions:

- Measure rating distributions overall and by category.
- Explore negative-review concentration by product area.
- Analyze review volume over time within the available date window.
- Compute text length statistics and review completeness metrics.
- Inspect frequent words and phrases in low-rated versus high-rated comments.
- Identify whether categories such as Camera or Battery are associated with repeated complaint themes.

Output of this stage:

- Exploratory analysis notebook or report
- Charts for ratings, categories, and complaint frequencies
- Initial hypotheses about key dissatisfaction drivers

## 4.4 Modeling

Goal: build models that convert review text into business insights.

Planned actions:

- Create a baseline sentiment label from the rating score.
- Build text-processing features from titles and comments.
- Train a sentiment classification model to predict positive, neutral, or negative review sentiment.
- Apply unsupervised theme discovery or keyword clustering to identify recurring complaint topics.
- Build a prioritization score that combines review rating, category, theme frequency, and usefulness count where available.

Expected modeling outputs:

- Sentiment classifier
- Complaint/theme groups
- Ranked issue dashboard inputs

## 4.5 Evaluation

Goal: confirm that the analytical outputs are accurate, useful, and actionable.

Planned actions:

- Evaluate sentiment classification using metrics such as accuracy, precision, recall, and F1-score.
- Review discovered complaint themes for business interpretability.
- Validate whether top-ranked issue categories match low-rating concentration in the raw data.
- Check for bias caused by short comments, sparse usefulness values, or category imbalance.
- Assess whether the final outputs support a clear action plan for product and support teams.

Output of this stage:

- Model evaluation summary
- Business interpretation of results
- Recommendations for deployment or iteration

## 5. Proposed Solution Summary

The proposed solution is a **Customer Review Intelligence System** that cleans raw review data, measures dissatisfaction across product areas, and highlights the most urgent complaint themes. For this dataset, the most suitable starting use case is:

**Prioritize the product issues that contribute most to low ratings, with special attention to categories that underperform, such as Camera.**

The solution would help stakeholders:

- Detect high-friction product features
- Prioritize engineering or quality-improvement efforts
- Improve product descriptions and customer communication
- Monitor whether future review batches show better sentiment outcomes

## 6. Conclusion

The raw Redmi 6 review dataset is sufficient to define a meaningful business problem and plan the full data science workflow. The strongest immediate opportunity is not long-term trend forecasting, but structured identification of dissatisfaction drivers from reviews, ratings, and categories. Before modeling, the dataset requires cleaning for encoding, type conversion, missing values, duplicates, and text standardization. Once prepared, it can support sentiment analysis, complaint theme discovery, and business prioritization of product issues.
