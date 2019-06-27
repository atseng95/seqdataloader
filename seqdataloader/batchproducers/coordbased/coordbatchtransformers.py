from __future__ import division, print_function, absolute_import
from .core import Coordinates


class AbstractCoordBatchTransformer(object):
  
    def __call__(self, coords):
        """
        Args:
            coords (:obj:`list` of :obj:`Coordinates` objects):

        Returns:
            another :obj:`list` of :obj:`Coordinates`
        """
        raise NotImplementedError()
    
    def chain(self, coord_batch_transformer):
        return lambda coords: coord_batch_transformer(self(coords))
      
      
class ReverseComplementAugmenter(AbstractCoordBatchTransformer):
    
    def __call__(self, coords):
        return coords + [x.get_revcomp() for x in coords]
      
      
class UniformJitter(AbstractCoordBatchTransformer):
  
    def __init__(self, maxshift, seed=1234, chromsizes_file=None):
        self.rng = np.random.RandomState(seed)
        self.maxshift = maxshift
        self.chromsizes = (
            self._read_chromsizes(chromsizes_file=chromsizes_file)
            if chromsizes_file is not None else None)
    
    def _read_chromsizes(self, chromsizes_file):
        chrom_to_size = {}
        for row in open(chromsizes_file):
            chrom,chromlen = row.rstrip().split("\t")
            chromlen = int(chromlen)
            chrom_to_size[chrom] = chromlen
        return chrom_to_size
   
    def __call__(self, coords):
        a_list = []
        for coord in coords:
            chrom = coord.chrom
            start = coord.start
            end = coord.end
            isplusstrand = coord.isplusstrand
            shift_size = int(self.rng.uniform(low=0, high=(2*self.maxshift + 1))
                             - self.maxshift)
            shift_size = max(-start, shift_size)
            if self.chromsizes is not None:
                shift_size = min(self.chromsizes[chrom]-end, shift_size)
            start = start + shift_size
            end = end + shift_size
            a_list.append(Coordinates(chrom=chrom, start=start,
                                      end=end, isplusstrand=isplusstrand))
        return a_list
