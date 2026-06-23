import torch
from typing import Dict, Any
from sklearn.metrics import f1_score, roc_auc_score


def count_parameters(net: torch.nn.Module) -> int:
    return sum(p.numel() for p in net.parameters() if p.requires_grad)


def accuracy(y_pred: torch.Tensor, y_true: torch.Tensor, threshold: float = 0.5) -> float:
    preds = (y_pred >= threshold).float()
    return round((preds == y_true).float().mean().item(), 4)


def f1(y_pred: torch.Tensor, y_true: torch.Tensor, threshold: float = 0.5) -> float:
    preds = (y_pred >= threshold).float().numpy()
    return round(float(f1_score(y_true.numpy(), preds, zero_division=0)), 4)


def auc(y_pred: torch.Tensor, y_true: torch.Tensor) -> float:
    try:
        return round(float(roc_auc_score(y_true.numpy(), y_pred.numpy())), 4)
    except ValueError:
        return float('nan')


def rmse(y_pred: torch.Tensor, y_true: torch.Tensor) -> float:
    return round(((y_pred - y_true) ** 2).mean().sqrt().item(), 4)


def mae(y_pred: torch.Tensor, y_true: torch.Tensor) -> float:
    return round((y_pred - y_true).abs().mean().item(), 4)


def evaluate(model, X_test: torch.Tensor, y_test: torch.Tensor, task: str) -> Dict[str, Any]:
    """Avalia o modelo e retorna métricas, nº de parâmetros treináveis e tempo de treino."""
    preds  = model.predict(X_test)
    # ClassicFuzzyModel expõe num_params=0 diretamente (sem atributo .net)
    n_params = getattr(model, 'num_params', None)
    if n_params is None:
        n_params = count_parameters(model.net)
    result: Dict[str, Any] = {
        'num_params':      n_params,
        'training_time_s': round(getattr(model, 'training_time', 0.0), 2),
    }
    if task == 'classification':
        p, t = preds.cpu(), y_test.cpu()
        result['accuracy'] = accuracy(p, t)
        result['f1']       = f1(p, t)
        result['auc']      = auc(p, t)
    else:
        p, t = preds.cpu(), y_test.cpu()
        result['rmse_mean'] = rmse(p, t)
        result['mae_mean']  = mae(p, t)
        H = p.shape[1] if p.dim() == 2 else 1
        for h in range(H):
            col = p[:, h] if p.dim() == 2 else p
            ref = t[:, h] if t.dim() == 2 else t
            result[f'rmse_h{h+1}'] = rmse(col, ref)
    return result
