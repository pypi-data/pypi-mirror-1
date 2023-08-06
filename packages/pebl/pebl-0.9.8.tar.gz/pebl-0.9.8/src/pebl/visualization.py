import pylab


def consensusmatrix_heatmap(consensus_matrix):
    """Visualize the consensus matrix  as a heatmap.
    
    The consensus matrix (or edge marginals) are the posterior probabilities
    (or confidences) for each possible edge.
    
    """
    
    pylab.matshow(consensus_matrix)
    pylab.colorbar()
    pylab.show()

# -------------------------------------------

import os, os.path
import tempfile
import time
from bisect import bisect
import shutil

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import simplejson
from pkg_resources import resource_filename

from numpy import exp
from pebl.util import rescale_logvalues

def plot(values, outfile):
    fig = Figure(figsize=(5,5))
    ax = fig.add_axes([0.18, 0.15, 0.75, 0.75])
    #ax.plot(values)
    ax.scatter(range(len(values)), values, edgecolors='None',s=10)
    ax.set_title("Scores (in sorted order)")
    ax.set_xlabel("Networks")
    ax.set_ylabel("Log score")
    ax.set_xbound(-20, len(values)+20)
    canvas = FigureCanvasAgg(fig)
    canvas.print_figure(outfile, dpi=80)

def network_image(net, outfile1, outfile2, node_positions, 
                  dot="dot", neato="neato"):
    # with network's optimal layout
    fd,fname = tempfile.mkstemp()
    net.as_dotfile(fname)
    os.system("%s -Tpng -o%s %s" % (dot, outfile1, fname))
    os.remove(fname)

    # with given layout
    net.node_positions = node_positions
    fd,fname = tempfile.mkstemp()
    net.as_dotfile(fname)
    os.system("%s -n1 -Tpng -o%s %s" % (neato, outfile2, fname))
    os.remove(fname)

def consensus_network_image(net, outfile, cm, node_positions):
    def colorize_edge(weight):
        colors = "9876543210"
        breakpoints = [.1, .2, .3, .4, .5, .6, .7, .8, .9]
        return "#" + str(colors[bisect(breakpoints, weight)])*6

    def node(n, position):
        s = "\t\"%s\"" % n.name
        if position:
            x,y = position
            s += " [pos=\"%d,%d\"]" % (x,y)
        return s + ";"

    nodes = net.nodes
    positions = node_positions

    dotstr = "\n".join(
        ["digraph G {"] + 
        [node(n, pos) for n,pos in zip(nodes, positions)] + 
        ["\t\"%s\" -> \"%s\" [color=\"%s\"];" % \
            (nodes[src].name, nodes[dest].name, colorize_edge(cm[src][dest])) \
            for src,dest in net.edges
        ] +
        ["}"]
    )

    fd,fname = tempfile.mkstemp()
    open(fname, 'w').write(dotstr)
    os.system("neato -n1 -Tpng -o%s %s" % (outfile, fname))
    os.remove(fname)


def result_html(result_, outdir, numnetworks=10):
    def jsonize_run(r):
        return {
            'start': time.asctime(time.localtime(r.start)),
            'end': time.asctime(time.localtime(r.end)),
            'runtime': round((r.end - r.start)/60, 3),
            'host': r.host
        }

    pjoin = os.path.join
    
    # make outdir if it does not exist
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # copy static files to outdir
    staticdir = resource_filename('pebl', 'resources/htmlresult')
    shutil.copy2(pjoin(staticdir, 'index.html'), outdir)
    shutil.copytree(pjoin(staticdir, 'lib'), pjoin(outdir, 'lib'))
   
    # change outdir to outdir/data
    outdir = pjoin(outdir, 'data')
    os.mkdir(outdir)

    post = result_.posterior
    numnetworks = numnetworks if len(post) >= numnetworks else len(post)
    topscores = post.scores[:numnetworks]
    norm_topscores = exp(rescale_logvalues(topscores))

    resultsdata = {
        'topnets_normscores': [round(s,3) for s in norm_topscores],
        'topnets_scores': [round(s,3) for s in topscores],
        'runs': [jsonize_run(r) for r in result_.runs],
    } 

    # write out results related data
    open(pjoin(outdir, 'result.data.js'), 'w').write("resultdata=" + simplejson.dumps(resultsdata))

    # create network images
    top = post[0]
    top.layout()
    for i,net in enumerate(post[:numnetworks]):
        network_image(
            net, 
            pjoin(outdir, "%s.png" % i), 
            pjoin(outdir, "%s-common.png" % i), 
            top.node_positions
        )

    # create consensus network images
    cm = post.consensus_matrix
    for threshold in xrange(10):
        consensus_network_image(
            post.consensus_network(threshold/10.0),
            pjoin(outdir, "consensus.%s.png" % threshold),
            cm, top.node_positions
        )
            
    # create score plot
    plot(post.scores, pjoin(outdir, "scores.png"))

        def create_network_image(self, post, numnetworks, outdir):
            pjoin = os.path.join

            top = post[0]
            top.layout()
            for i,net in enumerate(post[:numnetworks]):
                self.network_image(
                    net, 
                    pjoin(outdir, "%s.png" % i), 
                    pjoin(outdir, "%s-common.png" % i), 
                    top.node_positions
                )



