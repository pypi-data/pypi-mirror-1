import numpy as num
import scipy.cluster.vq as vq
import scipy.linalg.decomp as decomp

def clusterdistfun(x,c):
    n = x.shape[0]
    d = x.shape[1]
    nclusts = c.shape[0]
    D = num.zeros((nclusts,n))
    for i in range(nclusts):
        D[i,:] = num.sum((x - num.tile(c[i,:],[n,1]))**2,axis=1)
    return D

def furthestfirst(x,k,mu0=None,start='mean'):
    # number of data points
    n = x.shape[0]
    # data dimensionality
    d = x.shape[1]
    
    # returned centers
    mu = num.zeros((k,d))
    
    # initialize first center
    if num.any(mu0) == False:
        if start == 'mean':
            # choose the first mean to be the mean of all the data
            mu[0,:] = num.mean(x,axis=0)
        else:
            # choose a random point to be the first center
            i = num.floor(num.random.uniform(0,1,1)*n)[0]
            mu[0,:] = x[i,:]
    else:
        mu[0,:] = mu0
    
    # initialize distance to all centers to be infinity
    Dall = num.zeros((k,n))
    Dall[:] = num.inf

    for i in range(1,k):
        # compute distance to all centers from all points
        Dall[i-1,:] = num.sum((x - num.tile(mu[i-1,:],[n,1]))**2,axis=1)
        # compute the minimum distance from all points to the centers
        D = num.amin(Dall,axis=0)
        # choose the point furthest from all centers as the next center
        j = num.argmax(D)
        mu[i,:] = x[j,:]

    Dall[k-1,:] = num.sum((x - num.tile(mu[k-1,:],[n,1]))**2,axis=1)
    idx = num.argmin(Dall,axis=0)

    return (mu,idx)

def gmminit(x,k,weights=None,kmeansiter=20,kmeansthresh=.001):

    n = x.shape[0]
    d = x.shape[1]
    
    # initialize using furthest-first clustering
    (mu,idx) = furthestfirst(x,k,start='random')

    # use k-means, beginning from furthest-first
    (mu,dmin) = vq.kmeans(x,mu,kmeansiter,kmeansthresh)

    # get labels for each data point
    D = clusterdistfun(x,mu)
    idx = num.argmin(D,axis=0)

    # allocate covariance and priors
    S = num.zeros((d,d,k))
    priors = num.zeros(k)

    if num.any(weights) == False:
        # unweighted
        for i in range(k):
            # compute prior for each cluster
            nidx = num.sum(num.double(idx==i))
            priors[i] = nidx
            # compute mean for each cluster
            mu[i,:] = num.mean(x[idx==i,:],axis=0)
            # compute covariance for each cluster
            diffs = x[idx==i,:] - num.tile(mu[i,:].reshape(1,d),[nidx,1])
            S[:,:,i] = num.dot(num.transpose(diffs),diffs) / priors[i]
    else:
        # replicate weights
        weights = num.tile(weights.reshape(n,1),[1,d])
        for i in range(k):
            # compute prior for each cluster
            nidx = num.sum(num.double(idx==i))
            priors[i] = num.sum(weights[idx==i,0])
            # compute mean for each cluster
            mu[i,:] = num.sum(weights[idx==i,:]*x[idx==i,:],axis=0)/priors[i]
            # compute covariance for each cluster
            diffs = x[idx==i,:] - num.tile(mu[i,:].reshape(1,d),[nidx,1])
            diffs *= num.sqrt(weights[idx==i,:])
            S[:,:,i] = num.dot(num.transpose(diffs),diffs) / priors[i]

    # normalize priors
    priors = priors / num.sum(priors)

    # return
    return (mu,S,priors)

def gmm(x,k,weights=None,nreplicates=10,kmeansiter=20,kmeansthresh=.001,emiters=100,emthresh=.001,mincov=.01):
    # number of data points
    n = x.shape[0]
    # dimensionality of each data point
    d = x.shape[1]
    # initialize min error
    minerr = num.inf

    # replicate many times
    for rep in range(nreplicates):

        # initialize randomly
        (mu,S,priors) = gmminit(x,k,weights,kmeansiter,kmeansthresh)

        # optimize fit using EM
        (mu,S,priors,gamma,err) = gmmem(x,mu,S,priors,weights,emiters,emthresh,mincov)
        if err < minerr:
            mubest = mu
            Sbest = S
            priorsbest = priors
            minerr = err
            gammabest = gamma

    return (mubest,Sbest,priorsbest,gammabest,minerr)

def gmmmemberships(mu,S,priors,x,weights=1,initcovars=None):
    if initcovars is None:
        initcovars = S.copy()

    # number of data points
    n = x.shape[0]
    # dimensionality of data
    d = x.shape[1]
    # number of clusters
    k = mu.shape[0]

    # allocate output
    gamma = num.zeros((n,k))

    # normalization constant
    normal = (2.0*num.pi)**(num.double(d)/2.0)
    #print 'd = %d, normal = %f' % (d,normal)
    #print 'mu = '
    #print mu
    #print 'S = '
    #for j in range(k):
    #    print S[:,:,j]
    #print 'priors = '
    #print priors
    #print 'weights = '
    #print weights

    # compute the activation for each data point
    for j in range(k):
        #print 'j = %d' % j
        #print 'mu[%d,:] = '%j + str(mu[j,:])
        #print 'S[:,:,%d] = '%j + str(S[:,:,j])
        diffs = x - num.tile(mu[j,:],[n,1])
        #print 'diffs = '
        #print diffs
        try:
            c = decomp.cholesky(S[:,:,j])
        except num.linalg.linalg.LinAlgError:
            print 'S[:,:,%d] = '%j + str(S[:,:,j]) + ' is singular'
            print 'Reverting to initcovars[:,:,%d] = '%j + str(initcovars[:,:,j])
            S[:,:,j] = initcovars[:,:,j]
            c = decomp.cholesky(S[:,:,j])
        #print 'chol(S[:,:,%d]) = '%j + str(c)
        temp = num.transpose(num.linalg.solve(num.transpose(c),num.transpose(diffs)))
        #print 'temp = '
        #print temp
        gamma[:,j] = num.exp(-.5*num.sum(temp**2,axis=1))/(normal*num.prod(num.diag(c)))
        #print 'gamma[:,%d] = ' % j
        #print gamma[:,j]

    # include prior
    gamma *= num.tile(priors,[n,1])
    #print 'after including prior, gamma = '
    #print gamma

    # compute negative log likelihood
    e = -num.sum(num.log(num.sum(gamma,axis=1))*weights)
    #print 'e = %f' % e
    
    s = num.sum(gamma,axis=1)
    #print 's = '
    #print s
    # make sure we don't divide by 0
    s[s==0] = 1
    gamma /= num.tile(s.reshape(n,1),[1,k])
    #print 'gamma = '
    #print gamma
    
    return (gamma,e)    

def gmmupdate(mu,S,priors,gamma,x,weights=1,mincov=.01,initcovars=None):

    if num.any(initcovars) == False:
        initcovars = S
    
    # number of data points
    n = gamma.shape[0]
    # number of clusters
    k = gamma.shape[1]
    # dimensionality of data
    d = x.shape[1]

    gamma *= num.tile(weights.reshape(n,1),[1,k])

    # update the priors (note that it has not been normalized yet)
    priors[:] = num.sum(gamma,axis=0)    
    #print 'updated priors to ' + str(priors)

    # if any prior is to small, then reinitialize that cluster
    fixsmallpriors(x,mu,S,priors,initcovars,gamma)

    for i in range(k):
        # update the means
        mu[i,:] = num.sum(num.tile(gamma[:,i].reshape(n,1),[1,d])*x,axis=0)/priors[i]
        #print 'updated mu[%d,:] to '%i + str(mu[i,:])
        # update the covariances
        diffs = x - num.tile(mu[i,:],[n,1])
        diffs *= num.tile(num.sqrt(gamma[:,i].reshape(n,1)),[1,d])
        S[:,:,i] = (num.dot(num.transpose(diffs),diffs)) / priors[i]
        #print 'updated S[:,:,%d] to [%.4f,%.4f;%.4f,%.4f]'%(i,S[0,0,i],S[0,1,i],S[1,0,i],S[1,1,i])
        # make sure covariance is not too small
        if mincov > 0:
            [D,V] = num.linalg.eig(S[:,:,i])
            #print 'mineigval = %.4f'%num.min(D)
            if num.min(D) < mincov:
                S[:,:,i] = initcovars[:,:,i]
                #print 'reinitializing covariance'
                #print 'D = '
                #print D
                #print 'initcovars[:,:,%d] = [%.4f,%.4f;%.4f,%.4f]'%(i,initcovars[0,0,i],initcovars[0,1,i],initcovars[1,0,i],initcovars[1,1,i])
                
    # normalize priors
    priors /= num.sum(priors)
    #print 'normalized priors: ' + str(priors)

def gmmem(x,mu,S,priors,weights=None,niters=100,thresh=.001,mincov=.01):

    #print 'data = '
    #print x

    e = num.inf
    # store initial covariance in case covariance becomes too small
    if mincov > 0:
        for i in range(S.shape[2]):
            #print 'S initially is: '
            #print S[:,:,i]
            D, U = num.linalg.eig(S[:,:,i])
            #print "U = " + str(U)
            #print 'D = ' + str(D)
            D[D<mincov] = mincov
            #print 'D = ' + str(D)
            S[:,:,i] = num.dot(num.dot(U,num.diag(D)),U.transpose())
            #print 'S is now: '
            #print S[:,:,i]
    initcovars = S.copy()

    for iter in range(niters):

        # E-step: compute memberships
        [gamma,newe] = gmmmemberships(mu,S,priors,x,weights,initcovars)

        # M-step: update parameters
        gmmupdate(mu,S,priors,gamma,x,weights,mincov,initcovars)

        # if we've converged, break
        if newe >= e - thresh:
            break
        
        e = newe

    [gamma,e] = gmmmemberships(mu,S,priors,x,weights,initcovars)

    return (mu,S,priors,gamma,e)

def fixsmallpriors(x,mu,S,priors,initcovars,gamma=None):

    #print 'calling fixsmallpriors with: '
    #print 'mu = ' + str(mu)
    #print 'S = '
    #for i in range(S.shape[2]):
    #    print S[:,:,i]
    #print 'priors = ' + str(priors)
    #for i in range(initcovars.shape[2]):
    #    print 'initcovars[:,:,%d]: '%i
    #    print initcovars[:,:,i]
    #    print 'initcovars[:,:,%d].shape: '%i + str(initcovars[:,:,i].shape)
        
    MINPRIOR = .01
    issmall = priors < .01
    if not issmall.any():
        return

    n = x.shape[0]
    d = x.shape[1]
    k = mu.shape[0]

    normal = (2.0*num.pi)**(num.double(d)/2.0)

    if gamma is None:
        
        # compute the density for each x from each mixture component
        gamma = num.zeros((n,k))
        for i in range(k):
            diffs = x - num.tile(mu[i,:],[n,1])
            c = decomp.cholesky(S[:,:,i])
            temp = num.transpose(num.linalg.solve(num.transpose(c),num.transpose(diffs)))
            gamma[:,i] = num.exp(-.5*num.sum(temp**2,axis=1))/(normal*num.prod(num.diag(c)))
    # end gamma is None

    # loop through all small priors
    smalli, = num.where(issmall)
    for i in smalli:

        print 'fixing cluster %d with small prior = %f: '%(i,priors[i])

        # compute mixture density of each data point
        p = num.sum(gamma*num.tile(priors,[n,1]),axis=1)

        #print 'samples: '
        #print x
        #print 'density of each sample: '
        #print p

        # choose the point with the smallest probability
        j = p.argmin()

        print 'lowest density sample: x[%d] = '%j + str(x[j,:])

        # create a new cluster
        mu[i,:] = x[j,:]
        S[:,:,i] = initcovars[:,:,i]
        priors *= (1 - MINPRIOR)/(1.-priors[i])
        priors[i] = MINPRIOR

        print 'reset cluster %d to: '%i
        print 'mu = ' + str(mu[i,:])
        print 'S = '
        print S[:,:,i]
        print 'S.shape: ' + str(S[:,:,i].shape)
        print 'prior = ' + str(priors[i])

        # update gamma
        diffs = x - num.tile(mu[i,:],[n,1])
        c = decomp.cholesky(S[:,:,i])
        temp = num.transpose(num.linalg.solve(num.transpose(c),num.transpose(diffs)))
        gamma[:,i] = num.exp(-.5*num.sum(temp**2,axis=1))/(normal*num.prod(num.diag(c)))

#n0 = 100
#n1 = 100
#d = 3
#k = 2
#mu0 = num.array([0.,0.,0.])
#mu1 = num.array([5.,5.,5.])
#weights = num.hstack((10*num.ones(n0),num.ones(n1)))
#std0 = 1
#std1 = 1
#x0 = num.random.standard_normal(size=(n0,d))*std0 + num.tile(mu0,[n0,1])
#x1 = num.random.standard_normal(size=(n1,d))*std1 + num.tile(mu1,[n1,1])
#x = num.vstack((x0,x1))
#(mu,S,priors,err) = gmm(x,k,weights=weights)
#print 'centers = '
#print mu
#print 'covars = '
#print S[:,:,0]
#print S[:,:,1]
#print 'priors = '
#print priors
#print 'err = %f' % err
