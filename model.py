import torch
from torch import nn
from torch.nn.parameter import Parameter


class CompositionalEmbedding(nn.Module):
    r"""A simple compositional codeword and codebook that store embeddings.

     Args:
        num_embeddings (int): size of the dictionary of embeddings
        num_codebook (int): size of the codebook of embeddings
        num_codeword (int): size of the codeword of embeddings
        embedding_dim (int): size of each embedding vector

     Shape:
         - Input: (LongTensor): (N, W), W = number of indices to extract per mini-batch
         - Output: (Tensor): (N, W, embedding_dim)

     Attributes:
         - code (Tensor): the learnable weights of the module of shape
              (num_embeddings, num_codebook, num_codeword)
         - codebook (Tensor): the learnable weights of the module of shape
              (num_codebook, num_codeword, embedding_dim)

     Examples::
         >>> from torch.autograd import Variable
         >>> m = CompositionalEmbedding(20000, 16, 32, 64)
         >>> input = Variable(torch.randperm(128).view(16, -1))
         >>> output = m(input)
         >>> print(output.size())
         torch.Size([16, 8, 64])
     """

    def __init__(self, num_embeddings, num_codebook, num_codeword, embedding_dim):
        super(CompositionalEmbedding, self).__init__()
        self.num_embeddings = num_embeddings
        self.embedding_dim = embedding_dim
        self.code = Parameter(torch.Tensor(num_embeddings, num_codebook, num_codeword))
        self.codebook = Parameter(torch.Tensor(num_codebook, num_codeword, embedding_dim))

        nn.init.xavier_uniform(self.code)
        nn.init.xavier_uniform(self.codebook)

    def forward(self, input):
        return None

    def __repr__(self):
        return self.__class__.__name__ + ' (' + str(self.num_embeddings) + ', ' + str(self.embedding_dim) + ')'


class Model(nn.Module):
    def __init__(self, text, num_class):
        super().__init__()

        vocab_size = text.vocab.vectors.size(0)
        embed_dim = text.vocab.vectors.size(1)
        hidden_dim = 512

        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.encoder = nn.GRU(embed_dim, hidden_dim, num_layers=2, dropout=0.2, bidirectional=True)

        self.embedding.weight.data.copy_(text.vocab.vectors)
        self.embedding.weight.requires_grad = False

        self.linear = nn.Sequential(nn.Dropout(0.2), nn.Linear(hidden_dim * 2, num_class))

    def forward(self, x):
        embed = self.embedding(x)
        out, _ = self.encoder(embed)

        out = self.linear(out[-1])
        return out
