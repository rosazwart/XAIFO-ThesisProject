import drugdisease_fetcher as drugdisease_fetcher

if __name__ == "__main__":
    drug_disease_pairs = drugdisease_fetcher.load_drug_disease_entries()
    print(drug_disease_pairs.head(10))
    
    drugdisease_fetcher.load_phenotype_matcher()