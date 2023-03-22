%PLOT THE CLASSES OVER TIME FOR DART VERSION
Cum = zeros(11,5)
for run = 1:100
    run
    FILE = strcat('../results/SpectralDARTMaterialClassConvExp/ExpNAngles8ARMSIRT_CUDAStart2DART10ARM10Fix0.99/HistosRun', int2str(run), 'NoMat4noEnergies10.txt')    
    T = textread(FILE)
    Cum  = Cum + T
end

Avg = Cum/100

run = 1
FILE = strcat('../results/SpectralDARTMaterialClassConvExp/ExpNAngles8ARMSIRT_CUDAStart2DART10ARM10Fix0.99/RealHistoRun', int2str(run), 'NoMat4noEnergies10.txt');
T = textread(FILE);
T = transpose(T)

%Array for plotting horizontal lines with exact pixel classes amounts (in this case 0 2601 2455 2652 2564)
TRUEVALUESABS = T
TRUEVALUES = TRUEVALUESABS/(128*128);
Avg = Avg/(128*128);

figure
hold on
ylim([0.07, 0.21]);
for i = 0:4
    h(i+1) = plot([0:1:10],Avg(:,i+1), 'DisplayName', strcat('Material', int2str(i)), 'Marker', '.', 'MarkerSize', 20)
    c = get(h(i+1),'Color')
    c
    xL = get(gca,'xLim');
    k(i+1) = line(xL,[TRUEVALUES(i+1) TRUEVALUES(i+1)],'Color', c, 'Linestyle', '-.');
end 
title('Number over pixels per material class over time')
xlabel('Completed DART iterations')
ylabel('Fraction of pixels')
set(gca, 'XTick', [0:10])
legend(h(2:5), 'Location', 'southeast')
exportgraphics(gcf,'../results/EXP2PixelClassesDART.eps')
exportgraphics(gcf,'../results/EXP2PixelClassesDART.png','Resolution', 300)
hold off

%PLOT THE CLASSES OVER TIME FOR NONDART VERSION
FILE = strcat('../results/plots/SpectralDARTMaterialClassConvExp/ExpNAngles8ARMSIRT_CUDAStart2DART0ARM100Fix0.99/HistosRun', int2str(run), 'NoMat4noEnergies10.txt')
Avg = textread(FILE)

FILE = strcat('../results/plots/SpectralDARTMaterialClassConvExp/ExpNAngles8ARMSIRT_CUDAStart2DART0ARM100Fix0.99/RealHistoRun', int2str(run), 'NoMat4noEnergies10.txt');
T = textread(FILE);
T = transpose(T)

%Array for plotting horizontal lines with values 0 2601 2455 2652 2564 WITH SAME
TRUEVALUESABS = [0 2601 2455 2652 2564];
TRUEVALUES = TRUEVALUESABS/(128*128);
Avg = Avg/(128*128);

figure
hold on
ylim([0.07, 0.21]);
for i = 0:4
    Avg(:,i+1)
    h(i+1) = plot(10*[0:1:10],Avg(:,i+1), 'DisplayName', strcat('Material', int2str(i)), 'Marker', '.', 'MarkerSize', 20)
    c = get(h(i+1),'Color')
    c
    xL = get(gca,'xLim');
    k(i+1) = line(xL,[TRUEVALUES(i+1) TRUEVALUES(i+1)],'Color', c, 'Linestyle', '-.');
end 
title('Number over pixels per material class over ARM invocations')
xlabel('Completed ARM iterations')
ylabel('Fraction of pixels')
set(gca, 'XTick', [0:10:100])
legend(h(2:5), 'Location', 'southeast')
exportgraphics(gcf,'../results/plots/EXP2PixelClassesNONDART.eps')
exportgraphics(gcf,'../results/plots/EXP2PixelClassesNONDART.png','Resolution', 300)
hold off

%PLOT THE PIXEL ERROR OVER TIME
figure
hold on
P = textread('../results/plots/SpectralDARTMaterialClassConvExp/ExpNAngles8ARMSIRT_CUDAStart2DART0ARM100Fix0.99/PixelErrors1NoMat4noEnergies10.txt');
P = P/(128*128)
plot([0:10:101], transpose(P), 'DisplayName', 'Standard ARM', 'Marker', '.', 'MarkerSize', 20)
P = textread('../results/plots/SpectralDARTMaterialClassConvExp/ExpNAngles8ARMSIRT_CUDAStart2DART10ARM10Fix0.99/PixelErrors1NoMat4noEnergies10.txt');
P = P/(128*128)
plot([0:10:101], transpose(P), 'DisplayName', 'MC-DART', 'Marker', '.', 'MarkerSize', 20)
xlabel('Total ARM iterations')
ylabel('Fraction of mislabeled pixels')
title('Pixel error over time')
xlim([0, 100]);
ylim([0, 0.16]);
legend('Location', 'northeast')
exportgraphics(gcf,'../results/EXP2PixelErrorOverTime.eps')
exportgraphics(gcf,'../results/EXP2PixelErrorOverTime.png','Resolution', 300)
hold off