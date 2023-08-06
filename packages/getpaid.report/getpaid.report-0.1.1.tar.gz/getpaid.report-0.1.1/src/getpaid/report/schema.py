import datetime
import sqlalchemy as rdb

metadata = rdb.MetaData()
metadata.bind = rdb.create_engine('sqlite://')

def now( ):
    return datetime.datetime.now()

order_ids = rdb.Sequence('order_id_seq', metadata=metadata)

orders = rdb.Table( 
  "orders",
  metadata,
  rdb.Column("order_id",rdb.Integer(), primary_key=True ),
  rdb.Column("order_zid", rdb.Integer(), unique=True, nullable=False ),
  rdb.Column("billing_id", rdb.Integer,  rdb.ForeignKey('addresses.address_id') ),
  rdb.Column("ship_id", rdb.Integer, rdb.ForeignKey('addresses.address_id') ),
  rdb.Column("customer_id", rdb.Integer, rdb.ForeignKey('customers.customer_id'), nullable=False ),
  rdb.Column("creation_date", rdb.DateTime(timezone=True) ),
  rdb.Column("finance_status", rdb.Unicode(20) ),
  rdb.Column("fulfillment_status", rdb.Unicode(20) )
  )

## # not used  
## order_log = rdb.Table(
##   "order_log",
##   metadata,
##   rdb.Column("log_id", rdb.Integer, primary_key=True),
##   rdb.Column("order_id", rdb.Integer, rdb.ForeignKey('orders.order_id'), nullable=False ),
##   rdb.Column("changed_by", rdb.Unicode(20) ),
##   rdb.Column("change_date", rdb.DateTime( timezone=True) ),
##   rdb.Column("chage_kind", rdb.Unicode(30) ),
##   rdb.Column("comment", rdb.Unicode(90) ),  
##   rdb.Column("new_state", rdb.String(20) ),
##   rdb.Column("previous_state", rdb.String(20) ),  
##   rdb.Column("transition", rdb.String(20) )
##   )

items = rdb.Table( 
  "items",
  metadata,
  rdb.Column("item_id", rdb.Integer, primary_key=True ),
  rdb.Column("item_zid", rdb.String(40) ),
  rdb.Column("order_id",  rdb.Integer, rdb.ForeignKey('orders.order_id'), nullable=False ),
  rdb.Column("product_id", rdb.Integer, rdb.ForeignKey('products.product_id') ),
  rdb.Column("product_code", rdb.Unicode(200), nullable=False), 
  rdb.Column("name", rdb.UnicodeText, nullable=False),
  rdb.Column("description", rdb.UnicodeText, nullable=False), 
  rdb.Column("cost", rdb.Float(precision=2), nullable=False ),
  rdb.Column("quantity", rdb.Integer, nullable=False)
  )
  
products = rdb.Table( 
  "products",
  metadata,
  rdb.Column("product_id", rdb.Integer, primary_key=True ),
  rdb.Column("product_code",rdb.Unicode(200), unique=True, nullable=False ),
  rdb.Column("supplier_uid", rdb.Unicode(60) ),
  rdb.Column("content_uid", rdb.Integer, nullable=False ),  # five.intid reference
  rdb.Column("type", rdb.String(30), nullable=False ),
  rdb.Column("price", rdb.Float( precision=2), nullable=False ),
  rdb.Column("pick_bin", rdb.Unicode(35) ),
  rdb.Column("pallet", rdb.Unicode(35) ),
  rdb.Column("stock", rdb.Integer ), # actual units on hand in warehouse
  rdb.Column("stock_reserve", rdb.Integer )  # minus those that have been ordered  
)

inventory = rdb.Table(
  "product_inventory_log",
  metadata,
  rdb.Column('entry_id',   rdb.Integer, primary_key=True),
  rdb.Column('date',       rdb.DateTime, default=now ),
  rdb.Column("order_id",   rdb.Integer, rdb.ForeignKey('orders.order_id') ),
  rdb.Column("product_id", rdb.Integer, rdb.ForeignKey('products.product_id'), nullable=False),
  rdb.Column("quantity",   rdb.Integer, nullable=False ),
  rdb.Column("stock",      rdb.Integer, nullable=False ), 
  rdb.Column("action",     rdb.Unicode(15), nullable=False )
  )

customers = rdb.Table( 
  "customers",
  metadata,
  rdb.Column('customer_id', rdb.Integer, primary_key=True),
  rdb.Column('user_id', rdb.Unicode(80), nullable=True),
  rdb.Column('name', rdb.Unicode(100), nullable=True),
  rdb.Column('phone_number', rdb.Unicode(15) ),
  rdb.Column('email', rdb.Unicode(60) ),
  rdb.Column('marketing_preference', rdb.Boolean, default=False ),
  rdb.Column('email_html_format', rdb.Boolean )
  )
    
addresses = rdb.Table( 
  "addresses",
  metadata,
  rdb.Column("address_id", rdb.Integer, primary_key=True ),
  rdb.Column("first_line", rdb.Unicode(200), nullable=False ),
  rdb.Column("second_line", rdb.Unicode(200), nullable=True ),
  rdb.Column("city", rdb.Unicode(120), nullable=False ),
  rdb.Column("state", rdb.String(20), nullable=False ),
  rdb.Column("country", rdb.String(20), nullable=False ),
  rdb.Column("postal_code", rdb.String(10), nullable=False ),
  )


## # not used ...
## warehouses = rdb.Table(
##   "warehouses",
##   metadata,
##   rdb.Column("warehouse_id", rdb.Integer, primary_key=True ),
##   rdb.Column("address_id",  rdb.Integer, rdb.ForeignKey('addresses.address_id') ),
##   )

## outgoing_shipment = rdb.Table(
##   "outgoing_shipments",
##   metadata,
##   rdb.Column( "shipment_id",  rdb.Integer, primary_key=True),
##   rdb.Column( "order_id",  rdb.Integer, rdb.ForeignKey('orders.order_id') ),      
##   rdb.Column( "warehouse_id",  rdb.Integer, rdb.ForeignKey('warehouses.warehouse_id') ),
##   rdb.Column( "to_address", rdb.Integer, rdb.ForeignKey('addresses.address_id') ),
##   rdb.Column( "shipment_tracking", rdb.String(128) ),
##   )

def main( ):
    import sys    
    usage = "usage: %s database_uri"%(sys.argv[0])

    args = sys.argv[1:]
    if len(args) != 1:
        print usage
        sys.exit(1)
        
    db_uri = args[0]
    db = rdb.create_engine( db_uri , echo=True)
    
    metadata.bind = db
    metadata.drop_all( checkfirst=True )    
    metadata.create_all( checkfirst=True )
    
if __name__ == '__main__':
    main()

