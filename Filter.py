import collections
import math
import log

class Filter(object):

    def feed(self, value: float):
        pass

    def clear(self):
        pass


class MovingAverage(Filter):
    def __init__(self, samples: int = 5, detect_outliers: bool = True, outlier_factor=10.):
        self.samples = samples
        self.values = collections.deque()
        self.detect_outliers = detect_outliers
        self.outlier_factor = outlier_factor
        self.logger = log.get_logger("Filter_MVA")

    def mean(self):
        if len(self.values) < self.samples:
            return None

        result = float(0)
        for v in self.values:
            result += v
        return result / float(len(self.values))

    def mean_and_sd(self):
        mean = self.mean()
        if mean is None:
            return None, None
        sd = float(0)
        for v in self.values:
            sd += math.pow(abs(v - mean), 2)

        return mean, math.sqrt(sd / len(self.values))
    def feed(self, value: float):

        if self.detect_outliers and self.samples == len(self.values) and self.detect_outlier(value):
            mean, sd = self.mean_and_sd()
            self.logger.info("Outlier detected: {} - Mean: {} SD: {}".format(value, mean, sd))
            return mean

        if len(self.values) == self.samples:
            self.values.popleft()

        self.values.append(value)

        return self.mean()

    def clear(self):
        self.values.clear()

    def detect_outlier(self, value):
        mean, sd = self.mean_and_sd()
        x = abs(mean - value)
        return x > self.outlier_factor * sd
