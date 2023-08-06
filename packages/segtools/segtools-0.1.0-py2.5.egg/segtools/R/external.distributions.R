library(lattice)

read.distributions <- function(...) {
  res <- read.delim(...)
  res$label <- factor(res$label)    # adds a Levels attribute with the unique labels
  res
}

panel.histogram.precomp <- function(x, y, ...) {
  box.width <- diff(x[1:2])
  x <- x + (box.width/2)

  panel.barchart(x, y, box.width = box.width, ...)
}

strip.highlight.yellow <- function(which.given = 1,
                                   which.panel = NULL)
{
 # copy to new variable names that do not shadow variable names in
 # closure
 which.given.highlight <- which.given
 which.panel.highlight <- which.panel

 # generate closure
 strip.highlight.func <- function(which.given, which.panel, ..., bg = NULL) {
   bg <-
     if (which.given %in% which.given.highlight
         && which.panel %in% which.panel.highlight)
       "yellow"
     else
       trellis.par.get("strip.background")$col[which.given]

   strip.default(which.given, which.panel, ..., bg = bg)
 }

 strip.highlight.func
}


strip.highlight <- function(which.given = 1,
                           which.panel = NULL)
{
 # copy to new variable names that do not shadow variable names in
 # closure
 which.given.highlight <- which.given
 which.panel.highlight <- which.panel

 # generate closure
 strip.highlight.func <- function(which.given, which.panel, ..., bg = NULL) {
   bg <-
     if (which.given %in% which.given.highlight
         && which.panel %in% which.panel.highlight)
       trellis.par.get("strip.shingle")$col[which.given]
     else
       trellis.par.get("strip.background")$col[which.given]

   strip.default(which.given, which.panel, ..., bg = bg)
 }

 strip.highlight.func
}

# crap
strip.highlight.all <- function(which.given = 1,
                           which.panel = NULL)
{
   strip.default(which.given, which.panel, ..., bg = "yellow")
}

# precomputed histogram
histogram.precomp <-
  function(x = count ~ lower_edge | trackname + label,      # formula, explained in the lattice book
                # ~ means "is modeled by", as in y ~ x
                # So count is the y axis,  lower_edge is the x axis
                # | means conditioned on
                # So it makes a plot for every label and trackname
           data,
           inseg,
           scales = list(x = list(relation = "free"),           # leave the x-axis free (uncorrelated b/w panels)
                         y = list(log = TRUE, at = at.log(),    # make y logged
                             labels = labels.log())),           # also make the labels of y logged
           xlab = "value",
           panel = panel.histogram.precomp,
           border = "transparent",
           col = trellis.par.get("superpose.symbol")$col[1],
           strip = NULL,
           #strip = strip.highlight(which.given = c(1,2), which.panel = c(1:100)),
           #strip = strip.highlight(which.given = NULL, which.panel = NULL),
           ...)
{
  # defining a new lattice function: see D. Sarkar, _Lattice:
  # Multivariate Data Visualization with R,_ sec. 14.3.1;
  # https://stat.ethz.ch/pipermail/r-help/2008-December/182370.html

#   trellis.focus("panel", row = 2, column = 2)
#   trellis.par.set("strip.background" = list(col = "orange"))
#   trellis.unfocus()

  #rowdata <- c("#00ff00","#008800","#ff0000","#880000")
  #mymatrix <- matrix (rowdata, nrow = 2, ncol = 2)
  # the following changes the strip color for all panels
  #trellis.par.set("strip.background" = list(col = c("green","red")))

  if (is.null(strip)) {
    # XXX: better to use TRUE and FALSE rather than 0 or 1, then you can just
    # use if (inseg)
    strip <-
      if (inseg == 1)
        strip.highlight(which.given = c(1,2), which.panel = c(1:100))
      else
        strip.highlight(which.given = NULL, which.panel = NULL)
  }

  ocall <- sys.call(sys.parent())
  ocall[[1]] <- quote(histogram.precomp)    # quote simply returns its argument

  # this computes the sum of the counts, for the "all" label
  labelsums <- with(data, aggregate(count, list(trackname = trackname,
                                                lower_edge = lower_edge),
                                    sum))
  names(labelsums) <- sub("^x$", "count", names(labelsums))

  # sub = regular expression substitute: sub (pattern, replacement, x ....)
  labelsums$label <- "all"

  data.labelsums <- rbind(data, labelsums)
  # now we have all the data, including "all"

  ccall <- match.call()
  ccall[[1]] <- quote(xyplot)
  ccall$x <- x
  ccall$data <- data.labelsums
  #ccall$groups <- eval(substitute(groups), data, parent.frame())
  ccall$scales <- scales
  ccall$xlab <- xlab
  ccall$panel <- panel
  ccall$border <- border
  ccall$col <- col
  ccall$horizontal <- FALSE
  ccall$strip <- strip
  ccall$max.y <- max(data.labelsums$count, na.rm = TRUE)

  res <- eval.parent(ccall)
  res$call <- ocall
  res
}

# XXXX do once with x = * | trackname, groups = label, once with groups = trackname
