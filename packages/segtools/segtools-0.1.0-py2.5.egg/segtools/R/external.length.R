expected.len <- function(prob.loop) {
  prob.loop / (1 - prob.loop)
}

panel.violinplot <-
  function(x, y, ..., box.ratio, mark.prior = NULL, marks.posterior = NULL)
{
  if (!is.null(mark.prior)) {
    log10.mark.prior <- log10(mark.prior)
    panel.refline(v = log10.mark.prior, h = 0)
  }

  panel.rug(x, NULL, ..., end = 0.01)
  panel.violin(x, y, ..., box.ratio = box.ratio)
  panel.bwplot(x, y, ..., box.ratio = 0)

  if (!is.null(marks.posterior)) {
    log10.marks.posterior <- log10(marks.posterior)
    panel.points(log10.marks.posterior, seq_along(marks.posterior),
                 pch = "|", col = "black", cex = 3)
  }
}

# data: a data.frame with a row for each segment
#  seg: (factor) the segment label
#  len: (integer) the length of the segment
violinplot.length <-
  function(x = seg ~ len, data, nint = 100,
           scales = list(x = list(log = TRUE, at = at.log(),
                           labels = labels.log())),
           panel = panel.violinplot, expected.lens = NULL)
{
  marks.posterior <-
    if (is.null(expected.lens)) {
      NULL
    } else {
      expected.len(expected.lens)
    }

  bwplot(x, data, nint = nint, scales = scales, panel = panel,
         marks.posterior = marks.posterior)
}


# data: a data.frame with a row for each segment
#  seg: (factor) the segment label
#  len: (integer) the length of the segment
violinplot.tss <-
  function(x = seg ~ tss, data, nint = 100,
           scales = list(x = list(log = FALSE)),
           xlab = "segment length",
           panel = panel.violinplot, expected.lens = NULL)
{
  marks.posterior <-
    if (is.null(expected.lens)) {
      NULL
    } else {
      expected.len(expected.lens)
    }

  bwplot(x, data, nint = nint, scales = scales, xlab = xlab,
         panel = panel, marks.posterior = marks.posterior)
}

