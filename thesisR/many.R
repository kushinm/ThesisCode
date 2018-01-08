library(ggplot2)
require(reshape2)

manyData <- read.csv("lessKids.txt")

ggplot(melt(manyData[5:8]), aes(x=variable, y=value, fill = variable)) +
  geom_boxplot()

meltData <- melt(manyData[5:8]) 

#Kin
t.test(meltData$value[which(meltData$variable == "KinChange")],mu=0)

#Coop
t.test(meltData$value[which(meltData$variable == "CoopChange")],mu=0)

#Defect
t.test(meltData$value[which(meltData$variable == "DefectChange")],mu=0)

#Group
t.test(meltData$value[which(meltData$variable == "GroupChange")],mu=0)

