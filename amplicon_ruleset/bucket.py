from typing import Dict, Set

class ReadBucket():
    def __init__(self, primer: str, data: Dict[str, str]={}, ids: Set[str]=set()):
        # string of the primer sequence
        self.primer = primer
        # dictionary with keys --> id, values --> sequence
        self.data = data
        # set of ids
        self.ids = set()
        # dictionary with keys --> base index, values --> count of each base
        self.base_count = self.count_bases()
        # index of lowest threshold
        self.lowest_threshold_index = 0

    def __len__(self) -> int:
        return len(self.ids)
    
    def __getitem__(self, id: str) -> str:
        return self.data[id]
    
    def __contains__(self, id: str) -> bool:
        return id in self.data

    def add(self, id: str, sequence: str):
        # add id and sequence to data
        self.data[id] = sequence
        # add id to ids
        self.ids.add(id)
        # update base count
        for base in range(len(sequence)):
            if base not in self.base_count:
                self.base_count[base] = [0,0,0,0]
            if sequence[base] == 'A':
                self.base_count[base][0] += 1
            elif sequence[base] == 'C':
                self.base_count[base][1] += 1
            elif sequence[base] == 'G':
                self.base_count[base][2] += 1
            elif sequence[base] == 'T':
                self.base_count[base][3] += 1
        

    def get_ids(self) -> Set[str]:
        return self.ids
    
    def is_congruent(self, threshold: float=0.9) -> bool:
        """
        Returns true if the sequences in the bucket are congruent to each other for the given threshold.

        Parameters
        ----------
        threshold : float, optional
            % of bases that should be the same, by default 0.9

        Returns
        -------
        bool
            true if the sequences in the bucket are congruent to each other, else false
        """
        if "*" in self.primer:
            return True
        track_threshold = 1.0
        for position in self.base_count:
            max_base = max(self.base_count[position])

            if max_base/len(self) < track_threshold and position > 19 and position < 150:
                track_threshold = max_base/len(self)
                self.lowest_threshold_index = position

            if track_threshold < threshold:
                return False
        self.primer = self.primer + "*"
        return True
            

    def count_bases(self) -> Dict[int, int]:
        """
        Counts the number of each base in the bucket.
        
        Parameters
        ----------
        None

        Returns
        -------
        Dict[int, int]
            dictionary with keys --> base position, values --> count of each base
        """
        base_count = {}
        for id in self.ids:
            sequence = self.data[id]
            for position in range(len(sequence)):
                if position not in base_count:
                    base_count[position] = [0,0,0,0]
                if sequence[position] == 'A':
                    self.base_count[position][0] += 1
                elif sequence[position] == 'C':
                    self.base_count[position][1] += 1
                elif sequence[position] == 'G':
                    self.base_count[position][2] += 1
                elif sequence[position] == 'T':
                    self.base_count[position][3] += 1

        return base_count


    def create_consensus(self) -> str:
        """
        Returns string of consensus sequence for the bucket.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        str
            consensus sequence
        """
        bases_count = self.base_count
        consensus = ""
        for base in bases_count:
            max_base = bases_count[base].index(max(bases_count[base]))
            if max_base == 0:
                consensus += 'A'
            elif max_base == 1:
                consensus += 'C'
            elif max_base == 2:
                consensus += 'G'
            elif max_base == 3:
                consensus += 'T'

        return consensus
    
