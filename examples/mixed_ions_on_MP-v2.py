#! /usr/bin/env python

import time
import smact
import itertools

from multiprocessing import Pool;


element_list = smact.ordered_elements(1, 103)
elements = smact.element_dictionary(element_list)

max_n = 4
neutral_stoichiometries_threshold = 8
pauling_test_threshold = 0.0;

# Number of times to report progress during the counting loop.

count_progress_interval = 100

# Parameters for the threaded version of the code.

mp_use = True;
mp_processes = 4
mp_chunk_size = 10


# Function for counting oxidation-state combinations for a given set of elements.
# Suitable for use with the mapping functions of the multiprocessing.Pool class.

def count_element_combination(args):
    element_combination, n, neutral_stoichiometries_lookup_table = args
    
    count = 0;

    oxidation_states_list = [
        (element.symbol, oxidation_state, element.pauling_eneg) for element in element_combination
            for oxidation_state in element.oxidation_states
        ]
    
    for state_combination in itertools.combinations(oxidation_states_list, n):
        symbols = [x[0] for x in state_combination]
        oxidation_states = [x[1] for x in state_combination]
        pauling_electronegativities = [x[2] for x in state_combination]
    
        if smact.pauling_test(symbols, oxidation_states, pauling_electronegativities, threshold = pauling_test_threshold, repeat_anions = True, repeat_cations = True):
            count = count + neutral_stoichiometries_lookup_table[tuple(sorted(oxidation_states))]

    return count;


if __name__ == '__main__':
    # Obtain the unique oxidation states across all the elements considered.

    oxidation_states = set(
        oxidation_state for element in elements.values()
            for oxidation_state in element.oxidation_states
        );
    
    # List unique oxidation-state combinations for each set of n-element combinations.

    oxidation_state_combinations = {
        n : list(itertools.combinations_with_replacement(oxidation_states, n))
            for n in range(2, max_n + 1)
    }

    # Sort combinations and cast to tuples -- used as keys to a lookup table below.
    
    oxidation_state_combinations = {
        key : [tuple(sorted(item)) for item in value]
            for key, value in oxidation_state_combinations.items()
        }

    # Print the number of combinations of oxidation states for each value of n to be analysed.

    print "Combinations of known oxidation states:"
    
    for i in range(2, max_n + 1):
        print "m = {0}: {1}".format(i, len(oxidation_state_combinations[i]))

    print ""

    # Initialise a thread pool if required.
    
    thread_pool = Pool(processes = mp_processes) if mp_use else None

    for n in range(2, max_n + 1):
        # Lookup table with the number of charge-neutral stoichiometries for each combination of oxidation-states.
        # Uses the tuples in oxidation_state_combinations as keys.

        neutral_stoichiometries = {
            oxidation_states : len(list(smact.charge_neutrality_iter(oxidation_states, threshold = neutral_stoichiometries_threshold)))
                for oxidation_states in oxidation_state_combinations[n]
            }

        # Count and sum charge-neutral combinations of oxidation states for each of the combinations in element_combinations.

        start_time = time.time()

        # Count the number of element combinations - needed for the progress indicator.

        combination_count = sum(
            len([element_combination for element_combination in itertools.combinations(element_list, i)])
                for i in range(2, n + 1)
            );

        print "Counting ({0} element combinations)...".format(combination_count)

        # The combinations are counted in chunks set by count_progress_interval.

        batch_size = combination_count // count_progress_interval
        data_pointer = 0

        count = 0

        # Set up a generator expression to return combinations of elements.
        # Generators are evaluated lazily in Python, which avoids keeping all the combinations in memory - doing so can require quite a lot for large n (~300 Mb for quaternaries).
        # To count the combinations in chunks, a second generator expression is used in the while loop (below) which calls next() on the generator the required number of times.
        # As well as keeping memory usage fairly constant, this seems to carry little, if any, CPU overhead compared to creating and slicing a list.
        # So, it's perhaps a bit "filthy", but...

        combination_generator = (
            [elements[symbol] for symbol in element_combination]
                for i in range(2, n + 1)
                    for element_combination in itertools.combinations(element_list, i)
            )

        while data_pointer < combination_count:
            iterations = min(batch_size, combination_count - data_pointer)

            if mp_use:
                # Threaded code path -- iteration over element combinations is done using the multiprocessing.Pool.imap_unordered() function.
                
                count = count + sum(
                    thread_pool.imap_unordered(
                        count_element_combination, ((next(combination_generator), n, neutral_stoichiometries) for i in range(0, iterations)), chunksize = mp_chunk_size
                        )
                    )
            else:
                # Serial code path -- iteration over element combinations is done using the itertools.imap() function.
                
                count = count + sum(
                    itertools.imap(count_element_combination, ((next(combination_generator), n, neutral_stoichiometries) for i in range(0, iterations)))
                    )

            # After each chunk, report the % progress, elapsed time and an estimate of the remaining time.
            # The smact.pauling_test() calls take a variable amount of time, so the estimate of the remaining time is not always accurate, particularly for the first few cycles.

            data_pointer = data_pointer + iterations

            percent_done = 100.0 * float(data_pointer) / float(combination_count)

            time_elapsed = time.time() - start_time
            time_remaining = combination_count * (time_elapsed / data_pointer) - time_elapsed

            print "  -> {0}/{1} done ({2:.2f} %); {3:.2f} s elapsed, ~{4:.2f} s remaining".format(data_pointer, combination_count, percent_done, time_elapsed, time_remaining)

        print ""

        total_time = time.time() - start_time

        # Print results and total time for counting.

        print "Number of charge-neutral stoichiometries for combinations of {0} elements".format(n)
        print "(using known oxidation states, not including zero): {0}".format(count)
        print ""
       
        print "Total time for counting: {0:.3f} sec".format(total_time)
        print ""