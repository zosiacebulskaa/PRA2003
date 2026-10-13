import numpy as np
import matplotlib.pyplot as plt

########################################
# DICTIONARY: Bacterial Strains 🧫🆔
# Notes: List of valid IDs. 
########################################
bacterial_strains = { 
    "211": "E. coli (wild type)",
    "-211": "E. coli (mutant)",
    "321": "B. subtilis (wild type)",
    "-321": "B. subtilis (mutant)",
    "2212": "P. aeruginosa (wild type)",
    "-2212": "P. aeruginosa (mutant)",
    "3122": "S. pneumoniae (wild type)",
    "-3122": "S. pneumoniae (mutant)",
    "3312": "M. tuberculosis (wild type)",
    "-3312": "M. tuberculosis (mutant)",
    "3334": "S. enterica (wild type)",
    "-3334": "S. enterica (mutant)"
}

########################################
# FUNCTION: Calculate Momentum 🚗💨
# Notes: Use px, py, and pz components to return the momentum. 
########################################
def calculate_momentum(px, py, pz):
    ptotal = (px**2 + py**2 + pz**2) ** 0.5
    return ptotal

########################################
# FUNCTION: Process One File at a Time 🚗💨
# Notes: momentum_per_ID is a dictionary that stores all momenta for a given ID from one file
########################################
def process_file(filename):
    momentum_per_ID = {}

    # Create an empty list for each valid bacterial ID
    for bacterial_ID in bacterial_strains:
        momentum_per_ID[bacterial_ID] = []

    # Open and read one file
    with open(filename, "r") as infile:

        for line in infile:
            row = line.split()

            # Bacterial rows have at least 4 values: px, py, pz, ID (exclude headers)
            if len(row) >= 4:
                bacterial_ID = row[3]

                # Only calculate momentum for valid bacterial IDs
                if bacterial_ID in bacterial_strains:
                    px = float(row[0])
                    py = float(row[1])
                    pz = float(row[2])

                    ptotal = calculate_momentum(px, py, pz)

                    # Store momentum in the list for that ID
                    momentum_per_ID[bacterial_ID].append(ptotal)

    return momentum_per_ID

########################################
# Define Histogram Bins for each ID 📊✨
# Notes: E. coli: very large sample → finer bins, S. pneumoniae: smaller sample → wider bins
########################################
# Histogram bins for all six bacterial species
bins_per_species = {
    "211": np.arange(0, 61, 1),     # E. coli (bin width = 1 due to largest E. coli count)
    "321": np.arange(0, 61, 2),     # B. subtilis
    "2212": np.arange(0, 61, 2),    # P. aeruginosa
    "3122": np.arange(0, 62, 2),    # S. pneumoniae
    "3312": np.arange(0, 62, 2),    # M. tuberculosis
    "3334": np.arange(0, 62, 2)     # S. enterica
}

# Give each wild-type and mutant pair identical bins
bins_per_ID = {}

for wt_ID, bins in bins_per_species.items():
    bins_per_ID[wt_ID] = bins
    bins_per_ID[str(-int(wt_ID))] = bins

########################################
# FUNCTION: Make Histogram 📊✨
# Notes:  Converts momentum values for each ID into histogram bin counts for one file
########################################
def make_histogram(momentum_per_ID, bins_per_ID):
    histogram_counts = {}

    for bacterial_ID in bins_per_ID:
        counts, _ = np.histogram(
            momentum_per_ID[bacterial_ID],
            bins=bins_per_ID[bacterial_ID]
        )

        histogram_counts[bacterial_ID] = counts

    return histogram_counts

########################################
# FUNCTION: Count Valid Experiments 🧪💯
# Notes: Counts experiments containing at least one valid bacterial ID
########################################
def count_valid_experiments(filename):
    valid_event_count = 0

    with open(filename, "r") as infile:

        for header in infile:
            experiment_info = header.split()
            rows = int(experiment_info[1])

            valid_event = False

            # Go through all bacterial rows belonging to this experiment
            for _ in range(rows):
                row = next(infile)
                row_info = row.split()
                bacterial_ID = row_info[3]

                # Experiment is valid if at least one valid ID is present
                if bacterial_ID in bacterial_strains:
                    valid_event = True

            if valid_event:
                valid_event_count += 1

    return valid_event_count

########################################
# FUNCTION: Calculate Asymmetry ⚖️🦠
# Notes: Subtract the mutant histogram from the wild-type histogram bin by bin for one file
########################################
def calculate_asymmetry(wild_type_histogram, mutant_histogram):
    asymmetry = wild_type_histogram - mutant_histogram
    return asymmetry

########################################
# FUNCTION: Asymmetry Statistics ⚖️📈
# Notes: Calculates the mean asymmetry and standard deviation for each momentum bin across all 10 files
########################################
def asymmetry_statistics(asymmetry_data):

    # Combine asymmetry arrays from all 10 files into one array
    all_asymmetries = np.array([
        asymmetry_data[set_number]
        for set_number in range(1, 11)
    ])

    # Calculate mean and standard deviation for each momentum bin
    mean_asymmetry = np.mean(all_asymmetries, axis=0)
    std_asymmetry = np.std(all_asymmetries, axis=0, ddof=1)

    return mean_asymmetry, std_asymmetry

########################################
# FUNCTION: Find Bin Centers 🍩
# Notes: Calculate the midpoint of each histogram bin
########################################
def find_bin_centers(bins):
    bin_centers = (bins[:-1] + bins[1:]) / 2
    return bin_centers

########################################
# MAIN CODE (Using the Functions) 
########################################
all_histograms = {}

for set_number in range(1, 11):

    filename = f"PRA2003/output-Set{set_number}.txt"

    # Calculate and temporarily store the momentum values
    momentum_per_ID = process_file(filename)

    # Convert the momentum values into histogram counts
    histogram_counts = make_histogram(momentum_per_ID, bins_per_ID)

    # Save the histogram counts for this set
    all_histograms[set_number] = histogram_counts

    print(f"Set {set_number} complete.")




# Store normalized asymmetry for all species and all 10 sets
all_asymmetries = {}

for wt_ID in bins_per_species:
    all_asymmetries[wt_ID] = {}

for set_number in range(1, 11):

    filename = f"PRA2003/output-Set{set_number}.txt"

    # Number of valid experiments in this set
    n_experiments = count_valid_experiments(filename)

    for wt_ID in bins_per_species:

        mutant_ID = str(-int(wt_ID))

        # Calculate WT - mutant counts for each momentum bin
        raw_asymmetry = calculate_asymmetry(
            all_histograms[set_number][wt_ID],
            all_histograms[set_number][mutant_ID]
        )

        # Normalize by valid experiments BEFORE averaging across sets
        all_asymmetries[wt_ID][set_number] = (
            raw_asymmetry / n_experiments
        )

# Calculate mean and SD across the 10 sets
results = {}

for wt_ID, asymmetry_data in all_asymmetries.items():

    mean, std = asymmetry_statistics(asymmetry_data)
    bin_centers = find_bin_centers(bins_per_species[wt_ID])

    results[wt_ID] = {
        "mean": mean,
        "std": std,
        "bin_centers": bin_centers
    }

########################################
# PLOTS 📉📈
########################################

########################################
# PLOTS: All six bacterial species 📊
########################################

from scipy.optimize import curve_fit

plt.rcParams["font.family"] = "serif"

# Exponential decay function
def exponential_decay(momentum, A0, k):
    return A0 * np.exp(-k * momentum)


for wt_ID in bins_per_species:

    # Retrieve statistics for this species
    mean = results[wt_ID]["mean"]
    std = results[wt_ID]["std"]
    bin_centers = results[wt_ID]["bin_centers"]

    # Retrieve species name from our original dictionary
    species_name = bacterial_strains[wt_ID].replace(" (wild type)", "")

    # Fit exponential decay to mean asymmetry
    try:
        parameters, covariance = curve_fit(
            exponential_decay,
            bin_centers,
            mean,
            p0=[max(mean[0], 1e-6), 0.1],
            maxfev=10000
        )

        A0_fit, k_fit = parameters

        momentum_fit = np.linspace(
            min(bin_centers),
            max(bin_centers),
            500
        )

        asymmetry_fit = exponential_decay(
            momentum_fit, A0_fit, k_fit
        )

        print(f"{species_name}: A0 = {A0_fit}, k = {k_fit}")

    except RuntimeError:
        parameters = None
        print(f"Fit unsuccessful for {species_name}")

    # Create figure
    plt.figure(figsize=(10, 6))

    plt.errorbar(
        bin_centers,
        mean,
        yerr=std,
        fmt="o",
        capsize=3,
        color="indigo",
        ecolor="indigo",
        label="Mean asymmetry ± SD"
    )

    if parameters is not None:
        plt.plot(
            momentum_fit,
            asymmetry_fit,
            color="orchid",
            linewidth=2,
            label="Exponential decay fit"
        )

    plt.axhline(
        0,
        linestyle="--",
        color="indigo",
        alpha=0.7,
        label="Zero asymmetry"
    )

    plt.xlabel(r"Momentum, $p$ ($10^{-20}$ kg m s$^{-1}$)")
    plt.ylabel("Mean abundance asymmetry per valid experiment (WT − mutant)")
    plt.title(f"{species_name} abundance asymmetry as a function of momentum")

    plt.xticks(np.arange(0, 61, 5))
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    # Save each species as a separate image
    plt.savefig(
        f"asymmetry_{wt_ID}.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    # Print sum of the normalized momentum-bin asymmetries
    print(f"{species_name} integrated bin asymmetry: {np.sum(mean)}")
