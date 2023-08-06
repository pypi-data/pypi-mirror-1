function y = weighted_prctile(x,p,w,dim)
% WEIGHTED_PRCTILE Percentiles of a sample.
%   Y = WEIGHTED_PRCTILE(X,P,W) returns percentiles of the values in X.  P is a scalar
%   or a vector of percent values.  When X is a vector, Y is the same size
%   as P, and Y(i) contains the P(i)-th percentile.  When X is a matrix,
%   the i-th row of Y contains the P(i)-th percentiles of each column of X.
%   For N-D arrays, WEIGHTED_PRCTILE operates along the first non-singleton
%   dimension.
%
%   Y = WEIGHTED_PRCTILE(X,P,DIM) calculates percentiles along dimension DIM.  The
%   DIM'th dimension of Y has length LENGTH(P).
%
%   Percentiles are specified using percentages, from 0 to 100.  For an N
%   element vector X, WEIGHTED_PRCTILE computes percentiles as follows:
%      1) The sorted values in X are taken as the 100*(0.5/N), 100*(1.5/N),
%         ..., 100*((N-0.5)/N) percentiles.
%      2) Linear interpolation is used to compute percentiles for percent
%         values between 100*(0.5/N) and 100*((N-0.5)/N)
%      3) The minimum or maximum values in X are assigned to percentiles
%         for percent values outside that range.
%
%   WEIGHTED_PRCTILE treats NaNs as missing values, and removes them.
%
%   Examples:
%      y = weighted_prctile(x,50); % the median of x
%      y = weighted_prctile(x,[2.5 25 50 75 97.5]); % a useful summary of x
%
%   See also IQR, MEDIAN, NANMEDIAN, QUANTILE.

%   Copyright 1993-2004 The MathWorks, Inc.
%   $Revision: 2.12.4.5 $  $Date: 2004/06/25 18:52:56 $

if ~isvector(p) || numel(p) == 0
    error('stats:prctile:BadPercents', ...
          'P must be a scalar or a non-empty vector.');
elseif any(p < 0 | p > 100) || ~isreal(p)
    error('stats:prctile:BadPercents', ...
          'P must take real values between 0 and 100');
end

% Figure out which dimension prctile will work along.
sz = size(x);
if nargin < 4 
    dim = find(sz ~= 1,1);
    if isempty(dim)
        dim = 1; 
    end
    dimArgGiven = false;
else
    % Permute the array so that the requested dimension is the first dim.
    nDimsX = ndims(x);
    perm = [dim:max(nDimsX,dim) 1:dim-1];
    x = permute(x,perm);
    % Pad with ones if dim > ndims.
    if dim > nDimsX
        sz = [sz ones(1,dim-nDimsX)];
    end
    sz = sz(perm);
    dim = 1;
    dimArgGiven = true;
end

% If X is empty, return all NaNs.
if isempty(x)
    if isequal(x,[]) && ~dimArgGiven
        y = nan(size(p),class(x));
    else
        szout = sz; szout(dim) = numel(p);
        y = nan(szout,class(x));
    end

else
    % Drop X's leading singleton dims, and combine its trailing dims.  This
    % leaves a matrix, and we can work along columns.
    nrows = sz(dim);
    ncols = prod(sz) ./ nrows;
    x = reshape(x, nrows, ncols);
    y = zeros(numel(p), ncols, class(x));
    
    [x,order] = sort(x,1);
    nonnans = ~isnan(x);
    
    for j = 1:ncols,
      % make so that sum of wcurr(nonnan) = 100
      Z = sum(w(nonnans(:,j)));
      wcurr = 100*w(order(:,j))/Z;
    
      % find indices for each p
      cw = cumsum(wcurr(nonnans(:,j)));
      for i = 1:numel(p),
        idx1 = find(cw>=p(i),1);
        if isempty(idx1), 
          idx1 = nnz(nonnans(:,j));
        end
        if cw(idx1) ~= p(i) || idx1 == nnz(nonnans(:,j)),
          y(i,j) = x(idx1,j);
        else
          y(i,j) = (x(idx1,j)+x(idx1+1,j))/2;
        end
      end

    end
end

% undo the DIM permutation
if dimArgGiven
     y = ipermute(y,perm);  
end

% If X is a vector, the shape of Y should follow that of P, unless an
% explicit DIM arg was given.
if ~dimArgGiven && isvector(x)
    y = reshape(y,size(p)); 
end
