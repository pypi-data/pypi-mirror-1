from tensor import DenseTensor
import numpy

randmat = DenseTensor(numpy.random.normal(size=(100, 10)))
print randmat.k_means()

