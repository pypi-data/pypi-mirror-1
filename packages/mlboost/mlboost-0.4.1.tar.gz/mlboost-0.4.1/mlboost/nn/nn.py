#!/usr/bin/python
#  Copyright (C) 2009 Francis Pieraut <fpieraut@gmail.com>
#  Copyright (C) 2009 Pierre-Alexandre fournier <pafournier@gmail.com>
#  Copyright (C) 2009 Jeremy Barnes <jeremy@barneso.com>
#  Copyright (C) Neil Schemenauer <nas@arctrix.com>

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

''' Simple BackPropagation Neural Network module'''

# TODO: bias apply 
# TODO: link between optprop and energy

from numpy import *
from numpy.random import random, seed
import time
import pickle

seed(1)
# default learning rate, training epochs (iterations), optimization modes
_lr = 0.1
_epochs = 5
_mode = 'std'
_opt = True
MAX = 0.8

def randWeights(x, y, k=1.0):
    ''' calculate a random number where:  k <= rand < k '''
    return k * 2.0 * (random((x, y))-0.5)

def sigmoid(x):
    return 1.0/(1.0+exp(x))

def logsoftmax(outputs):
    
    softmax = exp(outputs)#/outputs.max())
    den = softmax.sum()
    logs = log(softmax / den)
    return logs

def dsigmoid(x):
    return x * (1-x)

def dlogsoftmax(x):
    ''' d'(logsoftmax) = 
        d'(log(e^x/sum(e^xi))=d'(log(e^x))-d'(log(sum(e^xi))=
        (d'(x - sum(xi))=d'(x-1)=1 '''
    return 1
    
def dtanh(x):
    ''' # derivative of our sigmoid function, in terms of the 
        output (i.e. y) '''
    return 1.0 - x**2

def derivative(fct):
    if fct == sigmoid:
        return dsigmoid
    elif fct == tanh:
        return dtanh
    elif fct == logsoftmax:
        return dlogsoftmax
    else:
        raise("unknown derivative %s" % fct)

def getsortedidx(error):
    n = len(error)
    idxe = random([n, 2])
    idxe[:,0]=arange(n)
    idxe[:,1]=array(abs(error),float)
    idxe.argsort()
    return idxe[:,0][::-1]

class NeuralNet:
    def __init__(self, ni, nh, no, outfct=None, verbose=True):
        ''' outfct activation output fct '''
        
        # set active fct and it derivate
        self.outfct = outfct or tanh
        self.doutfct = derivative(self.outfct)

        if (self.outfct == logsoftmax) and (no==1):
            raise("Need more than 1 output to use logsoftmax")
        if verbose:
            print "Creation of an NN <%s:%s:%s:%s>" \
                %(ni, nh, no, self.outfct.__name__)
        # number of input, hidden, and output nodes
        self.ni = ni + 1 # +1 for bias node
        self.nh = nh + 1 # +1 bor bias node
        self.no = no
        self.targets = zeros(no)
        
        # activations for nodes
        self.ai = array([1.0]*self.ni, float)
        self.ah = array([1.0]*self.nh, float)
        self.ao = array([1.0]*self.no, float)
        self.h = zeros(self.nh, float)
        self.o = zeros(self.no, float)

        # ensure bias = 1
        self.ai[-1] = 1
        self.ah[-1] = 1
        
        imax = 1.0/sqrt(ni)
        omax = 1.0/sqrt(nh)
        
        # create weights
        self.wi = randWeights(self.ni, self.nh, imax)
        self.wo = randWeights(self.nh, self.no, omax)
        
        # get bias reference for outputs and hidden
        self.bo = self.wo[-1,:]
        self.bh = self.wi[-1,:]

    def prob(self, i):
        return self.probs()[i]
        
    def probs(self):
        if self.outfct == logsoftmax:
            return exp(self.ao) * 100
        # otherwise simple normalization
        out = self.ao - self.ao.min()
        return out/out.sum() *100
            
    def hofprop(self, h, o, delta):
        ''' hidden -> output fprop() 
        WARNING: it assumes that std full fprop as been done prior
        to call this fct and only wo[h,o] has changed of delta. '''
        # self.ao = self.outfct(dot(self.ah, self.wo))
        self.o[o] += self.ah[h] * delta
        self.ao[o] = self.outfct(self.o[o])
        return self.ao

    def ihfprop(self, i, h, delta):
        ''' inputs -> hidden fprop() 
        WARNING: it assumes that std full fprop as been done prior
        to call this fct and only wo[i,h] has changed of delta. '''
        #self.ah[:-1] = tanh(dot(self.ai, self.wi[:,:-1]))
        #self.ao = self.outfct(dot(self.ah, self.wo))
        self.h[h] += self.ai[i] * delta
        before = self.ah[h]
        self.ah[h] = tanh(self.h[h])
    
        self.o += dot(self.ah[h]-before, self.wo[h,:])
        self.ao = self.outfct(self.o)
        return self.ao

    def fprop(self, inputs, opt=_opt, normalize=False):
        
        if len(inputs) != self.ni-1:
            raise ValueError, 'wrong number of inputs %s!=%s' \
                %(len(inputs), self.ni-1)
        
        if normalize:
            inputs = self.normalize_input(inputs)

        # set inputs
        self.ai[:-1] = array(inputs, float)
        
        # keep inputs reference (used in bprop optimized version)
        self.inputs = inputs
        
        if opt:
            self.h[:-1] = dot(self.ai, self.wi[:,:-1])
            self.ah[:-1] = tanh(self.h[:-1])
            self.o = dot(self.ah, self.wo)
            self.ao = self.outfct(self.o)
            if False:
                print "ah",self.ah
                print "wo",self.wo
                print "before", self.o
                print "bias",self.bo
                print "out",self.ao
                print "exp(out)",exp(self.ao)
            return self.ao
        
        if self.outfct == logsoftmax:
            print "warning logsoftmax not supported"

        # hidden activations
        for j in xrange(self.nh-1):
            sum = 0.0
            for i in xrange(self.ni):
                sum = sum + self.ai[i] * self.wi[i,j]
            self.h[j] = sum
            self.ah[j] = tanh(sum)

        # output activations
        for k in xrange(self.no):
            sum = 0.0
            for j in xrange(self.nh):
                sum = sum + self.ah[j] * self.wo[j,k]
            self.o = sum
            self.ao[k] = self.outfct(sum)
        
        return self.ao
    
    def init_bprop(self, target):
        ''' target is a class idx or the value in regression '''

        self.targets.fill(0)
        if self.outfct == tanh:
            self.targets.fill(-MAX)
        elif self.outfct == logsoftmax:
            self.targets.fill(log(1.0-MAX))
        
        # regression
        if self.no==1:
            self.targets[0] = target
        # classification
        else:
            if self.outfct == logsoftmax:
                self.targets[target] = log(MAX)
            else:
                self.targets[target] = MAX
    
    def bprop(self, target, lr=_lr, name='std', opt=_opt, mode=1):
        self.init_bprop(target)
        if name == 'std':
            self.bprop_std(self.targets, lr, opt)
        else:
            raise("unknown opt name %s" % name)   
        return self.cost(self.targets)
    
    def cost(self, targets):
        ''' compute mean error*error '''
        return (0.5 * (targets - self.ao) ** 2).sum()/self.no 

    def compute_output_deltas(self, targets):
        # calculate error terms for output
        oerror = targets - self.ao
        self.output_deltas = self.doutfct(self.ao) * oerror
        
        return self.output_deltas

    def compute_hidden_deltas(self, i=None):
        if i==None:
            # calculate error terms for hidden
            herror = dot(self.output_deltas, self.wo.T)
            self.hidden_deltas = dtanh(self.ah) * herror
        else:
            # calculate error terms for hidden i
            error = self.output_deltas[i]*self.wo[:,i]
            self.hidden_deltas = dtanh(self.ah) * error
            
        return self.hidden_deltas

    def compute_deltas(self, targets, i=None):
        ''' i is the ith class '''
        self.compute_output_deltas(targets)
        self.compute_hidden_deltas(i)
        return self.output_deltas, self.hidden_deltas

    def bprop_std(self, targets, lr=_lr, opt=_opt):

        self.compute_deltas(targets)

        if opt:
            self.wo += lr * dot(matrix(self.ah).T, 
                                matrix(self.output_deltas))
            self.wi += lr * dot(matrix(self.ai).T, 
                                matrix(self.hidden_deltas))
            return
                        
        # update output weights
        for j in range(self.nh):
            for k in range(self.no):
                self.wo[j,k] += lr * self.output_deltas[k] * self.ah[j]

        # update input weights
        for i in range(self.ni):
            for j in range(self.nh):
                self.wi[i,j] += lr * self.hidden_deltas[j] * self.ai[i]
        
    
    def normalize_input(self, inputs):
        ninputs = array(inputs, float)
        ninputs -= self.mu
        ninputs /= self.std
        return ninputs

    def result(self, outputs=None):
        if outputs == None:
            outputs = self.ao
        #outputs = outputs or self.ao
        if len(outputs) == 1:
            return outputs[0]
        else:
            try:
                return where (outputs == outputs.max())[0][0]
            except Exception, ex:
                print outputs,self.o,ex
                raise ex

        
    def test(self, patterns, opt=_opt, normalize=False):
        error = 0.0
        nbad = 0.0
        if len(patterns)==0:
            return -1
        for inputs, target in patterns:
            self.fprop(inputs, opt, normalize)
            if self.no == 1:
                if round(self.result())!=float(target):
                    nbad+=1
            elif self.result()!= target:
                    nbad+=1
            
        return nbad/len(patterns)*100

    def weights(self):
        print 'Input weights:'
        for i in range(self.ni):
            print self.wi[i]
        print
        print 'Output weights:'
        for j in range(self.nh):
            print self.wo[j]

    def save(self, fname):        
        f = open(fname, 'w')
        pickle.dump("n_inputs", f)
        pickle.dump(self.ni-1, f)
        pickle.dump("n_outputs", f)
        pickle.dump(self.no, f)
        pickle.dump("n_hidden", f)
        pickle.dump(self.nh-1, f)
        pickle.dump("std_inputs", f)
        pickle.dump(self.std, f)
        pickle.dump("mu_inputs", f)
        pickle.dump(self.mu, f)
        pickle.dump("weights_ho %s\n", f)
        pickle.dump(self.wo, f)
        pickle.dump("weight_ih", f)  
        pickle.dump(self.wi, f)
        pickle.dump("outfct", f)  
        pickle.dump(self.outfct.__name__, f)
        f.close()
            
    def train(self, patterns, patterns_val=None, bprop_name='std', 
              epochs=_epochs, lr=_lr, opt=_opt, mode=1, min_inc=0,
              verbose=True):
        ''' lr: learning rate  '''
        if verbose:
            print "training <bprop=%s:epoch=%s:mode=%s:out=%s>" % \
                (bprop_name, epochs, mode, self.outfct.__name__)
            print "# iteration rmse train-error% valid-error% time sec"
        patterns_val = patterns_val or patterns
        small_dataset = len(patterns) < 25
        
        t0 = time.clock()

        previous_valid_error = 101
        valid_error = 100

        i = 0

        def reach_min_inc():
            return (valid_error - previous_valid_error) < min_inc
        
        while reach_min_inc() and (i < (epochs+1)):
            i += 1
            error = 0.0
            nbad = 0.0
            for inputs, target in patterns:
                self.fprop(inputs, opt)
                error = error + self.bprop(target, lr, name = bprop_name, 
                                           opt=opt, mode=mode)
                if self.no == 1:
                    if round(self.result())!=float(target):
                        nbad+=1
                elif self.result()!= target:
                    nbad+=1

            previous_valid_error = valid_error
            valid_error  = self.test(patterns_val, opt)
            
            if (i % 100 == 0) or not small_dataset and verbose:
                print "#%5d %-8.6f %3.2f%% %3.2f%% %.2f sec" \
                    % (i, sqrt(error)/len(patterns),
                       nbad/len(patterns)*100, 
                       valid_error,
                       time.clock() - t0)

        if reach_min_inc() and verbose:
            print "reach minimum validation error increased"
    
def load_dataset(fname, validation=0.2, verbose=True, norm=True, test=0.1):
    ''' load flayers format dataset; return dataset, n_inputs, 
        n_outputs '''
    n_outputs = None
    f = open(fname, 'r')
    if fname[-4:]==".dat":
        splitter = ' '
        n_examples, n_inputs, n_outputs = \
            [int(x) for x in f.readline().strip().split(splitter)]
    else:
        splitter = ','
        header = f.readline().split(splitter)
        n_inputs = len(header) - 1

    records = f.readlines()
    n_examples = len(records)
    n_train = int(round((1.0 - validation - test) * n_examples))
    stop_valid = int(round((1.0 - test) * n_examples))
    val_p = validation * 100
    train_p = 100 - val_p - test*100
    output_choices = []
    if verbose:
        print "loading %s (train/validation/test=%s%%/%s%%/%s%%)" \
            %(fname, train_p, val_p, test*100)
    
    def get_dataset(records):
        ds = []
        # normalize inputs (-mu/std)
        mu = zeros(n_inputs)
        std = zeros(n_inputs)

        # compute mean
        for line in records:
            line = line.strip()
            inputs = array(map(float, line.split(splitter)[:-1]))
            label = int(line.split(splitter)[-1])
            if label not in output_choices:
                output_choices.append(label)
            mu += inputs
            ds.append([inputs, label])
        mu = mu/len(records)
    
        # compute std
        for inputs, target in ds:
            std += (inputs - mu)**2
    
        std = sqrt(std/len(records))
        min_mu = 0.001
        # replace std < limit by this limit
        idxs = where(mu < min_mu)
        if len(idxs):
            mu[idxs] = min_mu
        return ds, mu, std
    
    def normalize(ds, std, mu):
        # apply normalization
        for inputs, target in ds:
            inputs -= mu
            inputs /= std
        return ds
    
    # get training dataset
    tds, std, mu = get_dataset(records[:n_train])
    
    # get validation dataset
    vds, x, x = get_dataset(records[n_train:stop_valid])

    # get test dataset
    Tds, x, x = get_dataset(records[stop_valid:])
    if norm:
        normalize(tds, std, mu)
        normalize(vds, std, mu)
        normalize(Tds, std, mu)

    
    if not n_outputs:
        n_outputs = len(output_choices)
    
    return tds, std, mu, n_inputs, n_outputs, vds, Tds

def load(fname, verbose=True):
    f = open(fname, 'r')
    pickle.load(f)
    n_inputs = pickle.load(f)
    pickle.load(f)
    n_outputs = pickle.load(f)
    pickle.load(f)
    n_hidden = pickle.load(f)
    pickle.load(f)
    std = pickle.load(f)
    pickle.load(f)
    mu = pickle.load(f)
    pickle.load(f)
    wo = pickle.load(f)
    pickle.load(f)
    wi = pickle.load(f)
    pickle.load(f)
    outfct = globals()[pickle.load(f)]
    
    f.close()
    
    nn = NeuralNet(n_inputs, n_hidden, n_outputs, outfct, verbose = verbose)
    # set parameters
    nn.mu = mu
    nn.std = std
    nn.wo = wo
    nn.wi = wi
    return nn
    
def run(fname, bprop_name, epochs, n_hidden, lr, opt, outfct, 
        mode, validation=0.2, min_inc=0):
    tds, std, mu, n_inputs, n_outputs, vds, Tds = load_dataset(fname, validation)
    
    if validation == 0:
        print "Warning: validation is the training set"
        vds = tds

    nn = NeuralNet(n_inputs, n_hidden, n_outputs, outfct)
    nn.std = std
    nn.mu = mu
    # train it with some patterns
    nn.train(tds, vds, bprop_name, epochs, lr, opt, mode, min_inc)
    return nn
    
def test_logsoftmax():
    x = array(range(10))
    softmax = exp(logsoftmax(x))
    if (abs(softmax.sum() - 1.0) > 1e-10):
        raise("logsoftmax doesn't work %s!=1:\n%s" \
                  % (softmax.sum(), softmax) ) 

def test_save(verbose=False):
    nn = NeuralNet(16, 25, 10, verbose=verbose)
    nn.std = random(16)
    nn.mu = random(16)
    fname = '325345weafsdfast.save'
    nn.save(fname)
    nn_loaded = load(fname, verbose=verbose)
    import os
    os.remove(fname)
    inputs = random(16)

    if (nn.fprop(inputs) - nn_loaded.fprop(inputs)).sum() > 1e-9:
        raise("save doesn't work")

def test_fbprop(verbose=False):
    
    if verbose:
        print "unittest fprop"
    
    nn = NeuralNet(2, 2, 1, verbose=verbose)
    
    for input in [[0,0],[1,0],[0,1],[1,1]]:
        
        # fprop
        a = nn.fprop(input, False)
        b = nn.fprop(input, True)
        
        if verbose:
            print a, b
        if (a*100-b*100).round()!=0:
            raise("%s != %s" % (a, b))

    if verbose:
        print "unittest bprop"

    seed(1)
    nn1 = NeuralNet(2, 2, 2, verbose=verbose)
    seed(1)
    nn2 = NeuralNet(2, 2, 2, verbose=verbose)
     
    for target in [0,1]:  
        # bprop
        a = nn1.bprop(target, opt=True)
        b = nn1.bprop(target, opt=False)
        
        if verbose:
            print a, b
        if (a-b != 0) and (nn1.wi-nn2.wi).sum().round()!=0 and \
                ( (nn1.wo-nn2.wo).sum().round()!=0 ):
            raise("%s != %s" % (a, b))

def test_partial_fprop(verbose=False):
    seed(1)
    nn1 = NeuralNet(2, 2, 1, verbose=verbose)
    seed(1)
    nn2 = NeuralNet(2, 2, 1, verbose=verbose)
    i = 0
    h = 1
    o = 0
    delta = 0.1
    targets = array([1], float)
    inputs = array([1,0], float)
    nn1.wi[i,h] += delta
    out1 = nn1.fprop(inputs)[0]
    nn2.fprop(inputs)
    nn2.wi[i,h] += delta
    out2 = nn2.ihfprop(i, h, delta)[0]
    if not (abs(out1-out2) < 1e-10):
        raise("ihfprop doesnt work: %s!= %s" % (out1, out2))

    nn1.wo[h,o] += delta
    out1 = nn1.fprop(inputs)[0]
    nn2.wi[h,o] += delta
    out2 = nn2.hofprop(h,o,delta)[0]
    if not (abs(out1-out2) < 1e-10):
        raise("hofprop doesnt work: %s!= %s" % (out1, out2))

def main():
    
    from optparse import OptionParser
    parser = OptionParser(description = __doc__)
    parser.add_option("-b", "--bprop", dest="bprop_name", default='std',
                      help="bprop name: std, fraka1, fraka2, jeremy")
    parser.add_option("-m", "--mode", dest="mode", type=int, default=1,
                      help="mode of optimization")
    parser.add_option("--out", dest="outfct", default='tanh',
                      help="set outout fct (sigm,tanh,lsm)")
    parser.add_option("-n", "--no-opt", action="store_false",
                      dest="opt", default=globals()['_opt'],
                      help="set optimized fprop and bprop")
    parser.add_option("-l", "--lr", dest="lr", type=float, default=_lr,
                      help="set mode_learning rate")
    parser.add_option("-f", "--filename", dest="fname", 
                      default='letters.100.dat',
                      help="set dataset filename")
    parser.add_option("-s", "--save-filename", dest="save_fname", 
                      default='nn.save',
                      help="set save filename")
    parser.add_option("-L", "--load-filename", dest="load_fname", 
                      default=None, help="load nn filename")
    parser.add_option("--min-inc", dest="min_inc", default=0, type=float,
                      help="minimum validation increase to stop training")
    parser.add_option("--h", dest="n_hiddens", type=int, 
                      default=100, help="set nb of hidden neurons")
    parser.add_option("-e", "--epochs", dest="epochs", type=int, 
                      default=_epochs,
                      help="set number of epochs")
    parser.add_option('-v','--validation',dest='validation',type=float,
                      default=0.2, help="validation fraction")
    
    options, args = parser.parse_args()
    _opt = options.opt
    
    # unittests
    test_logsoftmax()
    test_fbprop()
    test_partial_fprop()
    test_save()
 
    if options.outfct == 'tanh':
        outfct = tanh
    elif options.outfct == 'sigm':
        outfct = sigmoid
    elif options.outfct == 'lsm':
        outfct = logsoftmax
    else:
        raise("unknow outfct %s" %options.outfct)
    
    if options.fname[-5:]=='.save':
        nn = load(options.fname)
    
    elif options.load_fname:
        nn = load(options.load_fname)
        tds, std, mu, vds, n_inputs, n_outputs = load_dataset(options.fname)
        print "training %s%%" % nn.test(tds, True, True)
        print "validation %s%%" % nn.test(vds, True, True)
    else:
        nn = run(options.fname, options.bprop_name, options.epochs, 
                 options.n_hiddens, options.lr, options.opt,
                 outfct, options.mode, validation=options.validation,
                 min_inc = options.min_inc)
    
        if options.save_fname:
            nn.save(options.save_fname)
            print "saved:%s" % options.save_fname
            tds, std, mu, n_inputs, n_outputs, vds, Tds = load_dataset(options.fname, verbose=False)
            nn_load = load(options.save_fname, verbose=False)
            t1, t2 = nn.test(tds) , nn_load.test(tds)
            v1, v2 = nn.test(vds),nn_load.test(vds)
            if v1!=v2 or t1!=t2:
                raise("loading problem")
            
            print "training %s%%" % t1
            print "validation %s%%" %v1 


if __name__ == '__main__':
    main()
