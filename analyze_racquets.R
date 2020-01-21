library(stringr)
library(cluster)
library(dendextend)

# dat<-read.table("racquets.tsv", sep = "\t", header = T, stringsAsFactors = F)
# dat<-dat[!duplicated(dat),]
# dat[dat=='None']<-NA
# 
# dat$Length.numeric<-str_extract(dat$Length, '(\\d)*(\\.\\d)*')
# dat$Head.Size.numeric<-str_extract(dat$Head.Size, '(\\d)*')
# dat$Weight.numeric<-str_extract(dat$Weight, '(\\d)*(\\.\\d)*')
# dat$Balance.Point.numeric <-str_extract(dat$Balance.Point, '(\\d)*(\\.\\d)*')
# 
# dat[, c("beam_head", "beam_shoulder", "beam_handle")]<-str_split(dat$Construction, "/", simplify = T)
# dat$beam_head<-str_extract(trimws(dat$beam_head), '(\\d)*')
# dat$beam_shoulder<-str_extract(trimws(dat$beam_shoulder), '(\\d)*')
# dat$beam_handle<-str_extract(trimws(dat$beam_handle), '(\\d)*')
# 
# dat[,c("nMain", "nCrosses")]<-str_split(dat$String.Pattern, "/", simplify = T)
# dat$nMain<-str_extract(trimws(dat$nMain), '(\\d)*')
# dat$nCrosses<-str_extract(trimws(dat$nCrosses), '(\\d)*')

dat<-read.table("racquets_clean.tsv", sep="\t", header=T, stringsAsFactors = F)

rownames(dat)<-dat$Name

dat$Brand<-str_split(dat$Name, " ", simplify = T)[,1]

dat_review_only<-dat[,c("Groundstrokes","Volleys","Serves","Returns","Power","Control","Maneuverability","Stability","Comfort","Touch.Feel","Topspin","Slice")]

dat_specs_only<-dat[,c("Length.numeric", "Head.Size.numeric", "Weight.numeric", "Balance.Point.numeric", "beam_head", "beam_shoulder", "beam_handle", "nMain", "nCrosses","Flex.Rating", "Swing.Weight")]

dat_review_specs<-dat[,c("Groundstrokes","Volleys","Serves","Returns","Power","Control","Maneuverability","Stability","Comfort","Touch.Feel","Topspin","Slice", "Length.numeric", "Head.Size.numeric", "Weight.numeric", "Balance.Point.numeric", "beam_head", "beam_shoulder", "beam_handle", "nMain", "nCrosses","Flex.Rating", "Swing.Weight")]

pdf("dendrograms.pdf", 5,7)

dat_review_only_daisy<-daisy(dat_review_only, metric="gower", stand=FALSE)
dat_specs_only_daisy<-daisy(dat_specs_only, metric = "gower", stand=TRUE)
dat_review_specs_daisy<-daisy(dat_review_specs, metric = "gower", stand=TRUE)

p<-c("steelblue1", "forestgreen", "darkorange2", "lawngreen", "black","darkmagenta", "gold3", "red1","deeppink2")

dat_review_only_cluster<-hclust(dat_review_only_daisy, method="ward.D2")
dat_review_only_dend<-as.dendrogram(dat_review_only_cluster)
par(cex=0.28, par(mai=c(0.2,0.2,0.4,0.8)))
labels_colors(dat_review_only_dend)<-p[as.numeric(as.factor(dat[dat_review_only_cluster$order, "Brand"]))]
plot(dat_review_only_dend, horiz = T, main= "TW Reviews Only", cex.main=4)

dat_specs_only_cluster<-hclust(dat_specs_only_daisy, method="ward.D2")
dat_specs_only_dend<-as.dendrogram(dat_specs_only_cluster)
par(cex=0.28, par(mai=c(0.2,0.2,0.4,0.8)))
labels_colors(dat_specs_only_dend)<-p[as.numeric(as.factor(dat[dat_specs_only_cluster$order, "Brand"]))]
plot(as.dendrogram(dat_specs_only_dend), horiz = T, main="TW Specs Only", cex.main=4)

dat_review_specs_cluster<-hclust(dat_review_specs_daisy, method="ward.D2")
dat_review_specs_dend<-as.dendrogram(dat_review_specs_cluster)
par(cex=0.28, par(mai=c(0.2,0.2,0.4,0.8)))
labels_colors(dat_review_specs_dend)<-p[as.numeric(as.factor(dat[dat_review_specs_cluster$order, "Brand"]))]
plot(as.dendrogram(dat_review_specs_dend), horiz = T, main="TW Reviews and Specs", cex.main=4)

dev.off()
