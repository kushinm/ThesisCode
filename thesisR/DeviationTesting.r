baseData <- read.csv("Dev Results/baseRand.csv")
brokenData <- read.csv("Dev Results/brokenRand.csv")
baseNullData <- read.csv("Dev Results/nullRand.csv")
brokenNullData <- read.csv("Dev Results/brokenNull5.csv")

for(i in seq(1,length(baseData))){
  bData <- baseData[[i]]
  brData <- brokenData[[i]]
  bnData <- baseNullData[[i]]
  #brnData <- brokenNullData[[i]]
  
  xlow <- min(c(bData,brData,bnData,brnData))-0.1
  xhigh <- max(c(bData,brData,bnData,brnData))+0.1
  hist(bData,col=rgb(1,0,0,0.25),xlim=c(xlow,xhigh),ylim=c(0,45),
       main=names(baseData)[i], xlab="Value", ylab="Frequency")
  hist(brData,col =rgb(0,1,0,0.25),add=T)
  hist(bnData,col =rgb(0,0,1,0.25),add=T)
  #hist(brnData,col =rgb(0,0,0,0.25),add=T)
  curve(dnorm(x,mean(bData),sd(bData)),add=TRUE,col="red")
  curve(dnorm(x,mean(brData),sd(bnData)),add=TRUE,col="green")
  curve(dnorm(x,mean(bnData),sd(brData)),add=TRUE,col="blue")
  #curve(dnorm(x,mean(brnData),sd(brnData)),add=TRUE,col="black")
  legend("topright",inset=c(0,0),title="Legend",c("Base","Reward+","BaseNull"),
         fill=c("red","green","blue"))
}
