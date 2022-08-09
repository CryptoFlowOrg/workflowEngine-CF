from models.config.baseConfigModel import BaseConfigModel


class ContractConfigModel(BaseConfigModel):
    abi = None
    address = None

    def transform(self):
        self.abi = self.raw['abi']
        self.address = self.raw['address']

    def isValid(self) -> bool:
        if self.abi is None or \
                self.address is None:
            return False
        return True
