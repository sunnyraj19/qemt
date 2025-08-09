import matplotlib.pyplot as plt
def plot_zne(xs, ys, mitigated, path: str):
    plt.figure()
    plt.scatter(xs, ys, label='Noisy measurements')
    plt.axhline(mitigated, linestyle='--', label=f'Mitigated={mitigated:.3f}')
    plt.xlabel('Noise scale (folds)'); plt.ylabel('Observable')
    plt.title('ZNE Extrapolation'); plt.legend(); plt.tight_layout()
    plt.savefig(path, dpi=150)


def plot_line(xs, ys, xlabel, ylabel, title, path: str):
    plt.figure()
    plt.plot(xs, ys, marker='o')
    plt.xlabel(xlabel); plt.ylabel(ylabel); plt.title(title)
    plt.tight_layout(); plt.savefig(path, dpi=150)

def plot_bar(labels, values, xlabel, ylabel, title, path: str):
    plt.figure()
    plt.bar(labels, values)
    plt.xlabel(xlabel); plt.ylabel(ylabel); plt.title(title)
    plt.tight_layout(); plt.savefig(path, dpi=150)
