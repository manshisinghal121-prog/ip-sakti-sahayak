import pandas as pd

file_path = "ml/dataset.csv"

new_data = [
    # Biodiversity_ABS
    ["Does using an Indian biological resource create access and benefit sharing obligations?", "Biodiversity_ABS"],
    ["What is access and benefit sharing under biodiversity regulations?", "Biodiversity_ABS"],
    ["When does the National Biodiversity Authority become relevant to a biological resource?", "Biodiversity_ABS"],
    ["Do I need biodiversity approval before commercializing a medicinal plant collected in India?", "Biodiversity_ABS"],
    ["What are the benefit sharing requirements for using an Indian medicinal plant?", "Biodiversity_ABS"],
    ["Does access to a biological resource for research trigger ABS requirements?", "Biodiversity_ABS"],
    ["What role does the NBA play when biological resources are used commercially?", "Biodiversity_ABS"],
    ["What is the connection between genetic resources and access and benefit sharing?", "Biodiversity_ABS"],
    ["Are biological resources obtained from India subject to biodiversity compliance?", "Biodiversity_ABS"],
    ["How does benefit sharing apply to traditional medicinal plants?", "Biodiversity_ABS"],
    ["What should an innovator check with the National Biodiversity Authority?", "Biodiversity_ABS"],
    ["Does commercial use of an Indian biological resource require ABS compliance?", "Biodiversity_ABS"],
    ["What permissions may be required for accessing biological resources in India?", "Biodiversity_ABS"],
    ["How are benefits shared when biological resources are commercially utilized?", "Biodiversity_ABS"],
    ["What biodiversity compliance should be checked before using a medicinal herb?", "Biodiversity_ABS"],

    # Traditional_Knowledge
    ["How can traditional Ayurvedic knowledge affect a patent application?", "Traditional_Knowledge"],
    ["How is traditional knowledge documented for intellectual property purposes?", "Traditional_Knowledge"],
    ["What is the role of TKDL in protecting traditional knowledge?", "Traditional_Knowledge"],
    ["Can previously documented traditional knowledge be considered prior art?", "Traditional_Knowledge"],
    ["Why is provenance important when documenting traditional knowledge?", "Traditional_Knowledge"],
    ["How can an Ayurveda formulation be distinguished from existing traditional knowledge?", "Traditional_Knowledge"],
    ["What intellectual property concerns arise from traditional medicinal knowledge?", "Traditional_Knowledge"],
    ["How does traditional knowledge influence novelty assessment?", "Traditional_Knowledge"],

    # Patentability
    ["What factors should be checked before filing a patent for a new herbal formulation?", "Patentability"],
    ["How do novelty and inventive step affect patentability of an Ayurvedic invention?", "Patentability"],
    ["Can a novel extraction process for a medicinal plant be patented?", "Patentability"],
    ["How should prior art be searched before applying for an herbal patent?", "Patentability"],
    ["What makes a new herbal formulation potentially patentable?", "Patentability"],
    ["Can an improved manufacturing method for an Ayurvedic product qualify for a patent?", "Patentability"],
    ["What patentability requirements apply to a new botanical composition?", "Patentability"]
]

new_df = pd.DataFrame(new_data, columns=["text", "label"])

df = pd.read_csv(file_path)

df = pd.concat([df, new_df], ignore_index=True)

df = df.drop_duplicates(subset=["text"])

df.to_csv(file_path, index=False)

print("Dataset updated successfully!")
print("Total rows:", len(df))
print("\nCategory counts:")
print(df["label"].value_counts())