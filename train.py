import torch, os
import torch.nn.functional as F
import torch.optim as optim
from torchvision import transforms

from data import PrepareDataset, Rescale, ToTensor, Normalize
from model import UNet


def train(epochs, batch_size, learning_rate):
    train_loader = torch.utils.data.DataLoader(
        PrepareDataset("data", train=True,
                       transform=transforms.Compose([
                           Normalize(),
                           Rescale(128),
                           ToTensor()
                       ]),
                       target_transform=transforms.Compose([
                           Normalize(),
                           Rescale(128),
                           ToTensor()
                       ])),
        batch_size=batch_size, shuffle=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = UNet().to(device)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(epochs):
        print('Epoch {}/{}'.format(epoch + 1, epochs))
        print('-' * 10)

        running_loss = 0.0
        for batch_idx, (images, masks) in enumerate(train_loader):
            images, masks = images.to(device), masks.to(device)

            optimizer.zero_grad()

            output = model(images)
            loss = F.binary_cross_entropy(output, masks)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        epoch_loss = running_loss / len(train_loader)
        print("Loss: {:.4f}\n".format(epoch_loss))

    os.makedirs("models", exist_ok=True)
    torch.save(model, "models/model.pt")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--epochs", type=int, default=1)
    parser.add_argument("-bs", "--batch_size", type=int, default=16)
    parser.add_argument("-lr", "--learning_rate", default=0.001)
    args = parser.parse_args()

    train(epochs=args.epochs,
          batch_size=args.batch_size,
          learning_rate=args.learning_rate)
