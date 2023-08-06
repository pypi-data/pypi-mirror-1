from getpaid.core.options import PersistentOptions
import interfaces

LuottokuntaOptions = PersistentOptions.wire("Luottokunta",
                                               "getpaid.luottokunta",
                                               interfaces.ILuottokuntaOptions )
