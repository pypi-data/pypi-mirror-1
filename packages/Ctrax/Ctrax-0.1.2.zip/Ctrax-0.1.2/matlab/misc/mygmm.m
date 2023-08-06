% [mu,S,priors] = mygmm(X,k,...)
% Input:
% X: N x D matrix of N D-dimensional data points
% k: number of clusters
% optional:
% 'Replicates' = 1
% 'CovarType' = 'full'
% 'display' = -1
% 'precision' = .0001
% 'ResetCovar' = 1
% 'MaxIters' = 100
% 'Start' = 'furthestfirst'
% 'distance' = 'sqEuclidean'
function [mu,S,priors,post] = mygmm(X,k,varargin)

[nreplicates,covartype,display,precision,resetcovar,maxiters,start,distance,weights] = ...
    myparse(varargin,'Replicates',1,'CovarType','full',...
            'display',-1,'precision',.0001,'ResetCovar',1,'MaxIters',100,...
            'Start','furthestfirst','Distance','sqEuclidean','weights',[]);
kmeansparams = {'Replicates',1,'Start',start,'Distance',distance,...
                'EmptyAction','singleton','Display','off','furthestfirst_start'};
if nreplicates == 1,
  kmeansparams{end+1} = 'mean';
else
  kmeansparams{end+1} = 'sample';
end
              
[N,D] = size(X);

options = foptions;
options(1) = display;
options(3) = precision;
options(5) = resetcovar;
options(14) = maxiters;

minerr = inf;
for replicate = 1:nreplicates,

  % initialize
  [idx,C] = mykmeans(X,k,kmeansparams{:});

  % create gmm structure
  mix = mygmminit(X,C,idx,covartype);

  if isempty(weights),
    [mix,options,errlog,post] = gmmem(mix,X,options);
  else
    [mix,options,errlog,post] = gmmem_weighted(mix,X,weights,options);
  end
  if errlog(end) < minerr,
    minerr = errlog(end);
    mixsave = mix;
  end;

end;

mu = mixsave.centres;
S = mixsave.covars;
priors = mixsave.priors;