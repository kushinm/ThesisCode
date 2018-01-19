library(ggplot2)
library(dplyr)

fileExtension <- "Gift Results/"
fileName <- "giftingDefault.txt"

ggData <- read.csv(paste(fileExtension,fileName,sep = ""),row.names=NULL)

#ggData[ggData$World==1,]

ggMeans <- ggData %>% group_by(Generation) %>% summarise_each(funs(mean))
ggSDs <- ggData %>% group_by(Generation) %>% summarise_each(funs(sd))
drops <- c("World","PopSize")
ggMeans <- ggMeans[ , !(names(ggMeans) %in% drops)]
ggSDs <- ggSDs[ , !(names(ggSDs) %in% drops)]
colnames(ggMeans) <- paste("Mean", colnames(ggMeans), sep = "_")
colnames(ggSDs) <- paste("SD", colnames(ggSDs), sep = "_")
colnames(ggMeans)[1] <- "Generation"
colnames(ggSDs)[1] <- "Generation"
DF <- merge(ggMeans,ggSDs,by="Generation")

#colnames(DF)

#DF <- ggData

ggplot(DF, aes(x = Generation, y = Mean_BaseRate))+
  geom_line(aes(y = Mean_BaseRate, color = "BaseRate"))+
  geom_line(aes(y = Mean_KinChange, color = "KinChange"))+
  geom_line(aes(y = Mean_CoopChange, color = "CoopChange"))+
  geom_line(aes(y = Mean_DefectChange, color = "DefectChange"))+
  geom_line(aes(y = Mean_GroupChange, color = "GroupChange"))+
  labs(y = "Value")+
  ggtitle(paste(fileName,"Means"))

ggplot(DF, aes(x = Generation, y = SD_BaseRate))+
  geom_line(aes(y = SD_BaseRate, color = "BaseRate"))+
  geom_line(aes(y = SD_KinChange, color = "KinChange"))+
  geom_line(aes(y = SD_CoopChange, color = "CoopChange"))+
  geom_line(aes(y = SD_DefectChange, color = "DefectChange"))+
  geom_line(aes(y = SD_GroupChange, color = "GroupChange"))+
  labs(y = "Value")+
  ggtitle(paste(fileName,"SDs"))#+
#theme(legend.position="none")

ggplot(DF, aes(x = Generation, y = Mean_BaseRate))+
  geom_line(aes(y = Mean_BaseRate, color = "BaseRate"))+
  geom_ribbon(aes(ymin=Mean_BaseRate-SD_BaseRate, ymax=Mean_BaseRate+SD_BaseRate, fill = "BaseRate"), alpha = 0.3)+
  geom_line(aes(y = Mean_KinChange, color = "KinChange"))+
  geom_ribbon(aes(ymin=Mean_KinChange-SD_KinChange, ymax=Mean_KinChange+SD_KinChange, fill = "KinChange"), alpha = 0.3)+
  geom_line(aes(y = Mean_CoopChange, color = "CoopChange"))+
  geom_ribbon(aes(ymin=Mean_CoopChange-SD_CoopChange, ymax=Mean_CoopChange+SD_CoopChange, fill = "CoopChange"), alpha = 0.3)+
  geom_line(aes(y = Mean_DefectChange, color = "DefectChange"))+
  geom_ribbon(aes(ymin=Mean_DefectChange-SD_DefectChange, ymax=Mean_DefectChange+SD_DefectChange, fill = "DefectChange"), alpha = 0.3)+
  geom_line(aes(y = Mean_GroupChange, color = "GroupChange"))+
  geom_ribbon(aes(ymin=Mean_GroupChange-SD_GroupChange, ymax=Mean_GroupChange+SD_GroupChange, fill = "GroupChange"), alpha = 0.3)+
  labs(y = "Value")+
  ggtitle(fileName)#+
#  theme(legend.position="none")

ggplot(DF, aes(x = Generation, y = Mean_CoopPercent))+
  geom_line(aes(y = Mean_CoopPercent, color = "CoopPercent"))+
  geom_ribbon(aes(ymin=Mean_CoopPercent-SD_CoopPercent, ymax=Mean_CoopPercent+SD_CoopPercent, fill = "CoopPercent"), alpha = 0.3)+
  geom_line(aes(y = Mean_DefectPercent, color = "DefectPercent"))+
  geom_ribbon(aes(ymin=Mean_DefectPercent-SD_DefectPercent, ymax=Mean_DefectPercent+SD_DefectPercent, fill = "DefectPercent"), alpha = 0.3)+
  labs(y = "Value")+
  ggtitle(paste(fileName,"Cooperation"))

#ggplot(ggData, aes(x = gens, y = Fitness))+
#  geom_line()

