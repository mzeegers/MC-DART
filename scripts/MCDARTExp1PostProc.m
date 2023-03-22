%Plotting of the results of the second experiment for the MC-DART paper
%Author,
%   Mathé Zeegers, 
%       Centrum Wiskunde & Informatica, Amsterdam (m.t.zeegers@cwi.nl)

%Maximaum number of materials (excl. background) and channels
sM = 10
sC = 10

%Compute the average pixel error for each material-channel combination
Cum = zeros(sM-1,sC);
for run = 1:100
    run
    FILE = strcat('../results/MCDARTMaterialChannelExp/ExpNAngles32ARMSIRT_CUDAStart10DART10ARM10Fix0.99/PixelErrors/pixelErrorRun', int2str(run), '.txt')
    T = textread(FILE);
    Cum  = Cum + T;
end
Avg = Cum/100;

%Normalize the results
Avg = Avg/(128*128) 

%Plot the results
figure
surf(Avg)
view(45,45)
title('Average pixel error of final segmentation')
xlabel('# Channels')
ylabel('# Materials')
xlim([1 10])
ylim([1 9])
set(gca, 'XTick', [1:sC])
set(gca, 'YTick', [1 2 3 4 5 6 7 8 9])
set(gca, 'YTickLabels', [2 3 4 5 6 7 8 9 10])
colorbar
exportgraphics(gcf,'../results/plots/EXP1PixelErrorOverMaterialsandChannels.eps')
exportgraphics(gcf,'../results/plots/EXP1PixelErrorOverMaterialsandChannels.png','Resolution', 300)
