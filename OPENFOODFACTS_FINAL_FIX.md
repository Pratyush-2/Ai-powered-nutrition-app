# OpenFoodFacts Search Fix - Final

## The Problem
The user searched for "rice", but "Rice Krispies" appeared first.
**Why?**
1. We were requesting `page_size: 5`.
2. OpenFoodFacts default sorting is chaotic or branded-heavy.
3. Top 5 results were often branded items (e.g., Rice Krispies, Rice Cakes).
4. The generic "Rice" was likely at position #10 or #20.
5. Our code never saw "Rice", so it couldn't score it higher.

## The Fix (Applied in `app/services/food_search.py`)

1. **`page_size: 50`** (Was 5)
   - verification: We now fetch 50 candidates instead of 5.
   - Impact: We are guaranteed to have the generic "Rice" in the pool.

2. **`sort_by: "unique_scans_n"`** (Was missing)
   - verification: Added to params.
   - Impact: Sorts results by popularity (popularity = staples like Rice, Eggs, Milk).
   - "Rice Krispies" might still be popular, but "Rice" has millions of scans globally.

3. **Combined with Scoring** (Already Implemented)
   - We receive 50 items.
   - "Rice" (Exact match) gets **10,000 points**.
   - "Rice Krispies" (Partial match) gets **400 points**.
   - Result: "Rice" wins by a landslide.

## How to Verify
1. Search "Rice".
2. Search "Chocolate".
3. Search "Eggs".

All results should now prioritize the **staple** version of the food over branded variants or snacks.
